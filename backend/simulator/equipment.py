import numpy as np

class SolarPanel:
    def __init__(self, capacity_kw=50, efficiency=0.15, area=300):
        self.capacity_kw = capacity_kw
        self.efficiency = efficiency
        self.area = area # m^2

    def get_power(self, irradiance_w_m2):
        # Power = irradiance * area * efficiency / 1000
        # Cap at capacity
        power = (irradiance_w_m2 * self.area * self.efficiency) / 1000.0
        return np.clip(power, 0, self.capacity_kw)

class WindTurbine:
    def __init__(self, rated_power_kw=100, cut_in=3.0, rated_speed=12.0, cut_out=25.0):
        self.rated_power_kw = rated_power_kw
        self.cut_in = cut_in
        self.rated_speed = rated_speed
        self.cut_out = cut_out

    def get_power(self, wind_speed_ms, temp_c):
        power = np.zeros_like(wind_speed_ms)
        
        mask_operating = (wind_speed_ms >= self.cut_in) & (wind_speed_ms <= self.cut_out)
        mask_below_rated = mask_operating & (wind_speed_ms < self.rated_speed)
        mask_above_rated = mask_operating & (wind_speed_ms >= self.rated_speed)
        
        # Cubic curve below rated
        if np.any(mask_below_rated):
            power[mask_below_rated] = self.rated_power_kw * ((wind_speed_ms[mask_below_rated] - self.cut_in) / (self.rated_speed - self.cut_in))**3
            
        if np.any(mask_above_rated):
            power[mask_above_rated] = self.rated_power_kw
            
        # Icing derate below -10 C
        derate_mask = temp_c < -10
        if np.any(derate_mask):
            # Derate linearly from 1.0 at -10C down to 0.5 at -40C
            derate_factor = np.clip(1.0 - ((-10 - temp_c) / 30.0) * 0.5, 0.5, 1.0)
            power = power * derate_factor
            
        return np.clip(power, 0, self.rated_power_kw)

class DieselGenerator:
    def __init__(self, capacity_kw=150, min_load_pct=0.3):
        self.capacity_kw = capacity_kw
        self.min_load_pct = min_load_pct
        self.min_stable_load_kw = capacity_kw * min_load_pct

    def get_fuel_consumption(self, load_kw, is_on):
        """Fuel consumption in L/h based on load."""
        if not is_on or load_kw <= 0:
            return 0.0
        
        # Simple quadratic or linear curve
        # Most efficient at 60-80% load
        load_pct = load_kw / self.capacity_kw
        if load_pct < self.min_load_pct:
            # Running below min stable load is highly inefficient and not recommended,
            # but if forced, penalize heavily.
            load_pct = self.min_load_pct
            
        # e.g., Base fuel + variable fuel
        base_fuel = 0.1 * self.capacity_kw # Liters just to run
        variable_fuel = 0.25 * (load_pct * self.capacity_kw)
        return base_fuel + variable_fuel

class Battery:
    def __init__(self, capacity_kwh=500, max_charge_kw=250, max_discharge_kw=250):
        self.capacity_kwh = capacity_kwh
        self.max_charge_kw = max_charge_kw
        self.max_discharge_kw = max_discharge_kw
        self.soc_kwh = capacity_kwh * 0.5 # start at 50%

    def get_derated_capacity(self, temp_c):
        """Derates capacity linearly below 0C."""
        if temp_c >= 0:
            return self.capacity_kwh
        derate = np.clip(1.0 - (0 - temp_c) * 0.015, 0.4, 1.0) # max 60% loss at -40C
        return self.capacity_kwh * derate

    def get_derated_charge_power(self, temp_c):
        """Derates charge power below 0C."""
        if temp_c >= 0:
            return self.max_charge_kw
        derate = np.clip(1.0 - (0 - temp_c) * 0.02, 0.2, 1.0) 
        return self.max_charge_kw * derate
