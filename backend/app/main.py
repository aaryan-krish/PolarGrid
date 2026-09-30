from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import datetime
import pandas as pd
import json
import os
import sys

from dotenv import load_dotenv
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

from motor.motor_asyncio import AsyncIOMotorClient
db = None
if MONGODB_URI and "<username>" not in MONGODB_URI:
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client.polargrid_database
        print("✅ Configured MongoDB Telemetry Connection!")
    except Exception as e:
        print("❌ MongoDB connection error:", e)

# Import custom modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.state import state
from simulator.equipment import DieselGenerator, Battery
from optimizer.baseline import BaselineController
from optimizer.pyomo_model import solve_dispatch
from modules.polar import calculate_autonomy, check_blizzard, AnomalyDetector
from ml.forecast import Forecaster

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "station_year.csv")
sim_data = None
forecaster = None
anomaly_detector = AnomalyDetector()
gen_model = DieselGenerator()

if os.path.exists(data_path):
    sim_data = pd.read_csv(data_path, parse_dates=["time"])
    # Train anomaly detector on some data
    anomaly_detector.train(
        [gen_model.get_fuel_consumption(load, True) for load in sim_data['load_kw'][:1000]], 
        sim_data['load_kw'][:1000].values
    )

try:
    forecaster = Forecaster(os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml"))
except:
    pass

class ToggleLoadRequest(BaseModel):
    enabled: bool

class ModeRequest(BaseModel):
    mode: str

@app.get("/api/status")
def get_status():
    return {
        "timestamp": state.timestamp.isoformat(),
        "mode": state.mode,
        "load_kw": state.load_kw,
        "solar_kw": state.solar_kw,
        "wind_kw": state.wind_kw,
        "generator_kw": state.generator_kw,
        "generator_on": state.generator_on,
        "battery_soc_pct": state.battery_soc_pct,
        "battery_kw": state.battery_kw,
        "battery_temp_c": state.battery_temp_c,
        "fuel_litres": state.fuel_litres,
        "ambient_temp_c": state.ambient_temp_c,
        "wind_speed_ms": state.wind_speed_ms,
        "blizzard_mode": state.blizzard_mode
    }

@app.get("/api/forecast")
def get_forecast(hours: int = 48):
    if not state.forecast_data:
        return {"generated_at": state.timestamp.isoformat(), "step_minutes": 60, "points": []}
        
    points = []
    for row in state.forecast_data[:hours]:
        points.append({
            "time": row['time'].isoformat() if isinstance(row['time'], datetime.datetime) else pd.to_datetime(row['time']).isoformat(),
            "load_kw": float(row['load_kw']),
            "solar_kw": float(row['solar_kw']),
            "wind_kw": float(row['wind_kw'])
        })
    return {
        "generated_at": state.timestamp.isoformat(),
        "step_minutes": 60,
        "points": points
    }

@app.get("/api/schedule")
def get_schedule():
    if not state.schedule_data:
        return {"horizon_hours": 48, "est_fuel_litres": 0.0, "points": []}
        
    points = []
    est_fuel = 0.0
    for p in state.schedule_data:
        points.append({
            "time": (state.timestamp + datetime.timedelta(hours=p['time_idx'])).isoformat(),
            "generator_kw": float(p['generator_kw']),
            "battery_kw": float(p['battery_kw']),
            "deferred_load_kw": float(p['deferred_load_kw']),
            "soc_pct": float(p['soc_pct'])
        })
        est_fuel += gen_model.get_fuel_consumption(p['generator_kw'], p['generator_kw'] > 0)
        
    return {
        "horizon_hours": len(points),
        "est_fuel_litres": est_fuel,
        "points": points
    }

@app.get("/api/autonomy")
def get_autonomy():
    # Avg daily burn: assume last 24h burn. Since we don't track it precisely, estimate:
    # Say we used (ai_fuel_l / sim_hour) per hour -> * 24 for daily
    if state.sim_hour > 0:
        avg_burn = (state.ai_fuel_l / state.sim_hour) * 24
    else:
        avg_burn = 100.0
        
    return calculate_autonomy(state.fuel_litres, avg_burn, 30) # Assume 30 days to resupply

@app.get("/api/alerts")
def get_alerts():
    return state.alerts

@app.get("/api/comparison")
def get_comparison():
    days = state.sim_hour / 24.0
    ai_fuel = state.ai_fuel_l
    base_fuel = state.baseline_fuel_l
    
    saved = 0.0
    if base_fuel > 0:
        saved = ((base_fuel - ai_fuel) / base_fuel) * 100
        
    return {
        "period_days": round(days, 2),
        "fuel_saved_pct": round(saved, 2),
        "baseline": {
            "fuel_litres": round(base_fuel, 2),
            "generator_hours": state.baseline_gen_hours,
            "renewable_pct": 50.0 # Dummy for now
        },
        "ai": {
            "fuel_litres": round(ai_fuel, 2),
            "generator_hours": state.ai_gen_hours,
            "renewable_pct": 55.0 # Dummy for now
        },
        "series": state.series
    }

@app.get("/api/loads")
def get_loads():
    return state.loads

@app.post("/api/loads/{id}/toggle")
def toggle_load(id: str, req: ToggleLoadRequest):
    for l in state.loads:
        if l["id"] == id:
            l["enabled"] = req.enabled
            return l
    return {"error": "Load not found"}

@app.post("/api/mode")
def set_mode(req: ModeRequest):
    if req.mode in ["AI", "BASELINE", "SAFE"]:
        state.mode = req.mode
    return {"mode": state.mode}

active_connections = set()

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            await asyncio.sleep(2) # we broadcast from the loop
            await websocket.send_json(get_status())
    except:
        active_connections.remove(websocket)

async def simulation_loop():
    global sim_data, forecaster
    
    baseline_controller = BaselineController()
    
    # We need an independent baseline state
    base_soc = 250.0
    
    if sim_data is None:
        return
        
    # Start at row 7300 (test set)
    start_idx = 7300
    state.sim_hour = 0
    state.fuel_litres = 10000.0
    
    while True:
        await asyncio.sleep(2.0)
        
        idx = start_idx + state.sim_hour
        if idx >= len(sim_data):
            idx = start_idx # loop
            
        row = sim_data.iloc[idx]
        
        # Realized truth
        state.timestamp = row['time']
        state.ambient_temp_c = row['ambient_temp_c']
        state.wind_speed_ms = row['wind_speed_ms']
        state.solar_kw = row['solar_kw']
        state.wind_kw = row['wind_kw']
        state.battery_temp_c = state.ambient_temp_c + 5.0 # Battery room is warmer
        
        # Aggregate load
        active_load = 0.0
        deferrable_loads = []
        for l in state.loads:
            if l['enabled']:
                active_load += l['kw']
                if l['priority'] == 'deferrable':
                    deferrable_loads.append(l)
                    
        # Just use row['load_kw'] as base critical load + our modeled loads
        # To make it dynamic, let's say the synthetic load_kw is the base, and we add deferrable
        total_required_load = row['load_kw'] # This already includes daily pattern
        
        # Run Baseline (for comparison tracking)
        b_gen_kw, b_batt_kw, b_soc, b_shed = baseline_controller.step(
            total_required_load, state.solar_kw, state.wind_kw, base_soc, state.battery_temp_c)
        base_soc = b_soc
        b_fuel = gen_model.get_fuel_consumption(b_gen_kw, b_gen_kw > 0)
        state.baseline_fuel_l += b_fuel
        if b_gen_kw > 0:
            state.baseline_gen_hours += 1
            
        # AI Mode logic
        actual_gen_kw = 0.0
        actual_batt_kw = 0.0
        
        try:
            if state.mode == "AI" and forecaster is not None:
                # Get past 48h data
                past_data = sim_data.iloc[idx-48:idx]
                future_weather = sim_data.iloc[idx:idx+48]
                
                # Predict
                forecast = forecaster.predict(state.timestamp, past_data, future_weather, hours=48)
                state.forecast_data = forecast.to_dict('records')
                
                # Check blizzard
                is_blizzard = check_blizzard(forecast['wind_speed_ms'].values)
                state.blizzard_mode = is_blizzard
                if is_blizzard and not any(a['type'] == 'blizzard' for a in state.alerts):
                    state.alerts.append({
                        "id": f"BLZ-{state.sim_hour}",
                        "time": state.timestamp.isoformat(),
                        "severity": "warning",
                        "type": "blizzard",
                        "message": "Blizzard forecast in next 24h. Initiating pre-charge."
                    })
                    
                # Pyomo Dispatch
                # We need to map our forecast into lists
                f_load = forecast['load_kw'].values.tolist()
                f_solar = forecast['solar_kw'].values.tolist()
                f_wind = forecast['wind_kw'].values.tolist()
                f_temp = forecast['ambient_temp_c'].values.tolist()
                
                # If blizzard, maybe we increase min SOC or force charge
                # For simplicity, we just pass to Pyomo.
                
                schedule, _ = solve_dispatch(
                    48, f_load, f_solar, f_wind, f_temp, state.battery_soc_kwh,
                    deferrable_loads=deferrable_loads
                )
                
                if schedule:
                    state.schedule_data = schedule
                    # Implement first step
                    actual_gen_kw = schedule[0]['generator_kw']
                    actual_batt_kw = schedule[0]['battery_kw']
                    state.battery_soc_kwh = schedule[0]['soc_kwh']
                else:
                    # Fallback if Pyomo fails
                    state.mode = "SAFE"
                    
            if state.mode in ["BASELINE", "SAFE"]:
                # Use our Baseline Controller logic for the actual state
                a_gen_kw, a_batt_kw, a_soc, a_shed = baseline_controller.step(
                    total_required_load, state.solar_kw, state.wind_kw, state.battery_soc_kwh, state.battery_temp_c)
                actual_gen_kw = a_gen_kw
                actual_batt_kw = a_batt_kw
                state.battery_soc_kwh = a_soc
                
        except Exception as e:
            print("Error in simulation step:", e)
            state.mode = "SAFE"
            
        # Update State
        state.generator_kw = actual_gen_kw
        state.generator_on = actual_gen_kw > 0
        state.battery_kw = actual_batt_kw
        state.battery_soc_pct = (state.battery_soc_kwh / 500.0) * 100
        state.load_kw = total_required_load
        
        # Consume fuel
        fuel_consumed = gen_model.get_fuel_consumption(actual_gen_kw, state.generator_on)
        state.ai_fuel_l += fuel_consumed
        state.fuel_litres -= fuel_consumed
        if state.generator_on:
            state.ai_gen_hours += 1
            
        # Anomaly Check
        if anomaly_detector.check_anomaly(total_required_load, fuel_consumed):
            if not any(a['type'] == 'leak' for a in state.alerts):
                state.alerts.append({
                    "id": f"LEAK-{state.sim_hour}",
                    "time": state.timestamp.isoformat(),
                    "severity": "critical",
                    "type": "leak",
                    "message": "Anomalous fuel consumption detected."
                })
        
        # Series for comparison chart (store once per day, or we can just append daily averages)
        if state.sim_hour % 24 == 0:
            state.series.append({
                "day": state.sim_hour // 24,
                "baseline_fuel_l": state.baseline_fuel_l,
                "ai_fuel_l": state.ai_fuel_l
            })
            
        # MongoDB Telemetry Save
        if db is not None:
            telemetry_doc = get_status()
            asyncio.create_task(db.telemetry.insert_one(telemetry_doc))
            
            # Also save any new alerts
            if state.alerts:
                # We can just update or insert them. For simplicity, save the latest alerts state.
                asyncio.create_task(db.alerts.replace_one({"_id": "latest_alerts"}, {"alerts": state.alerts}, upsert=True))
            
        state.sim_hour += 1

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulation_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
