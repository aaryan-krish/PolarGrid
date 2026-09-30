import datetime

class GlobalState:
    def __init__(self):
        self.timestamp = datetime.datetime.now()
        self.mode = "AI" # AI, BASELINE, SAFE
        self.load_kw = 0.0
        self.solar_kw = 0.0
        self.wind_kw = 0.0
        self.generator_kw = 0.0
        self.generator_on = False
        self.battery_soc_pct = 50.0
        self.battery_soc_kwh = 250.0
        self.battery_kw = 0.0
        self.battery_temp_c = 0.0
        self.fuel_litres = 10000.0
        self.ambient_temp_c = 0.0
        self.wind_speed_ms = 0.0
        self.blizzard_mode = False
        
        self.alerts = []
        self.loads = [
            {"id": "L1", "name": "Critical Station Systems", "priority": "critical", "kw": 50.0, "enabled": True},
            {"id": "L2", "name": "Science Lab Heating", "priority": "deferrable", "kw": 30.0, "enabled": True},
            {"id": "L3", "name": "Vehicle Block Heater", "priority": "deferrable", "kw": 20.0, "enabled": True}
        ]
        
        self.forecast_data = []
        self.schedule_data = []
        
        # Cumulative comparison
        self.sim_hour = 0
        self.ai_fuel_l = 0.0
        self.baseline_fuel_l = 0.0
        
        self.ai_gen_hours = 0
        self.baseline_gen_hours = 0
        
        self.ai_ren_pct = 0.0
        self.baseline_ren_pct = 0.0
        
        self.series = []

state = GlobalState()
