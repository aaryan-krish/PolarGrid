import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.state import state
from simulator.equipment import DieselGenerator
from optimizer.baseline import BaselineController
from optimizer.pyomo_model import solve_dispatch
from ml.forecast import Forecaster
import asyncio

async def evaluate():
    data_path = os.path.join(os.path.dirname(__file__), "data", "station_year.csv")
    if not os.path.exists(data_path):
        print("Data not found")
        return
        
    sim_data = pd.read_csv(data_path, parse_dates=["time"])
    forecaster = Forecaster(os.path.join(os.path.dirname(__file__), "ml"))
    
    gen_model = DieselGenerator()
    baseline_controller = BaselineController()
    
    start_idx = 7300
    # Simulate for 3 days (3 * 24 = 72 hours)
    sim_hours = 72 
    
    base_soc = 250.0
    ai_soc = 250.0
    
    baseline_fuel = 0.0
    ai_fuel = 0.0
    
    print("Running evaluation for 14 days...")
    
    for i in range(sim_hours):
        idx = start_idx + i
        if idx >= len(sim_data):
            break
            
        row = sim_data.iloc[idx]
        timestamp = row['time']
        ambient_temp = row['ambient_temp_c']
        wind_speed = row['wind_speed_ms']
        solar_kw = row['solar_kw']
        wind_kw = row['wind_kw']
        batt_temp = ambient_temp + 5.0
        
        load = row['load_kw']
        
        # 1. Baseline
        b_gen, b_batt, b_soc, b_shed = baseline_controller.step(
            load, solar_kw, wind_kw, base_soc, batt_temp)
        base_soc = b_soc
        baseline_fuel += gen_model.get_fuel_consumption(b_gen, b_gen > 0)
        
        # 2. AI
        past_data = sim_data.iloc[idx-48:idx]
        future_weather = sim_data.iloc[idx:idx+48]
        
        # Predict
        forecast = forecaster.predict(timestamp, past_data, future_weather, hours=48)
        
        f_load = forecast['load_kw'].values.tolist()
        f_solar = forecast['solar_kw'].values.tolist()
        f_wind = forecast['wind_kw'].values.tolist()
        f_temp = forecast['ambient_temp_c'].values.tolist()
        
        schedule, _ = solve_dispatch(
            48, f_load, f_solar, f_wind, f_temp, ai_soc, deferrable_loads=[]
        )
        
        if schedule:
            a_gen = schedule[0]['generator_kw']
            a_batt = schedule[0]['battery_kw']
            ai_soc = schedule[0]['soc_kwh']
        else:
            # Fallback
            a_gen, a_batt, a_soc, a_shed = baseline_controller.step(
                load, solar_kw, wind_kw, ai_soc, batt_temp)
            ai_soc = a_soc
            
        ai_fuel += gen_model.get_fuel_consumption(a_gen, a_gen > 0)
        
        if (i+1) % 24 == 0:
            print(f"Day {(i+1)//24}: Baseline Fuel={baseline_fuel:.1f} L, AI Fuel={ai_fuel:.1f} L")
            
    print("\n--- Final Results ---")
    print(f"Baseline Fuel: {baseline_fuel:.1f} L")
    print(f"AI Fuel:       {ai_fuel:.1f} L")
    if baseline_fuel > 0:
        saved = (baseline_fuel - ai_fuel) / baseline_fuel * 100
        print(f"Fuel Saved:    {saved:.1f}%")

if __name__ == "__main__":
    asyncio.run(evaluate())
