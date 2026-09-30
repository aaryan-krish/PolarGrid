import pandas as pd
import numpy as np

class BaselineController:
    """
    A simple rule-based controller.
    Generator turns on if renewable power + battery can't meet load.
    Battery charges if there's excess renewable power.
    No forecasting.
    """
    def __init__(self, battery_cap=500, gen_cap=150, min_gen_load=0.3):
        self.battery_cap = battery_cap
        self.gen_cap = gen_cap
        self.min_gen_load = min_gen_load * gen_cap
        
    def step(self, load_kw, solar_kw, wind_kw, current_soc, batt_temp_c):
        """Returns generator_kw, battery_kw (positive = charge), new_soc, shed_load."""
        
        # Derate battery
        derated_cap = self.battery_cap
        if batt_temp_c < 0:
            derated_cap = max(0.4 * self.battery_cap, self.battery_cap * (1.0 - (0 - batt_temp_c) * 0.015))
            
        derated_pwr = 250
        if batt_temp_c < 0:
            derated_pwr = max(0.2 * 250, 250 * (1.0 - (0 - batt_temp_c) * 0.02))

        # We need to serve load_kw
        net_load = load_kw - (solar_kw + wind_kw)
        
        generator_kw = 0.0
        battery_kw = 0.0
        shed_load = 0.0
        
        if net_load > 0:
            # We need more power
            # Try battery first
            available_discharge = min(current_soc, derated_pwr)
            if available_discharge >= net_load:
                battery_kw = -net_load
            else:
                # Need generator
                generator_kw = max(self.min_gen_load, net_load)
                generator_kw = min(generator_kw, self.gen_cap)
                
                # Re-evaluate balance
                power_surplus = (solar_kw + wind_kw + generator_kw) - load_kw
                if power_surplus > 0:
                    # Charge battery with surplus
                    battery_kw = min(power_surplus, derated_cap - current_soc, derated_pwr)
                elif power_surplus < 0:
                    # Try battery for the rest
                    shortfall = -power_surplus
                    batt_discharge = min(current_soc, derated_pwr, shortfall)
                    battery_kw = -batt_discharge
                    if batt_discharge < shortfall:
                        shed_load = shortfall - batt_discharge
        else:
            # We have excess renewable power
            power_surplus = -net_load
            battery_kw = min(power_surplus, derated_cap - current_soc, derated_pwr)
            # Generator off
            generator_kw = 0.0
            
        new_soc = current_soc + battery_kw
        return generator_kw, battery_kw, new_soc, shed_load
