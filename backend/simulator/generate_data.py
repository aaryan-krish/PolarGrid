import pandas as pd
import numpy as np
import os

def generate_year_data(output_path="data/station_year.csv"):
    """Generates 1 year of hourly synthetic data for a polar station."""
    np.random.seed(42)
    hours = 8760
    
    # Time index
    start_time = pd.Timestamp("2024-01-01 00:00:00")
    time_index = pd.date_range(start_time, periods=hours, freq="h")
    
    # Ambient temperature (-5 to -40 C)
    # Sinusoidal seasonal variation (coldest in July) + daily variation + noise
    day_of_year = time_index.dayofyear.values
    seasonal_temp = -22.5 - 17.5 * np.cos(2 * np.pi * (day_of_year - 200) / 365.25) 
    daily_temp = 3 * np.sin(2 * np.pi * time_index.hour.values / 24)
    noise_temp = np.random.normal(0, 2, hours)
    ambient_temp_c = np.clip(seasonal_temp + daily_temp + noise_temp, -50, 5)
    
    # Wind speed (katabatic winds, occasional blizzards)
    # Weibull distribution
    wind_speed_ms = np.random.weibull(2, hours) * 8
    # Add some blizzards (high wind for consecutive hours)
    for _ in range(10): # 10 blizzards a year
        start_blizzard = np.random.randint(0, hours - 72)
        duration = np.random.randint(24, 72)
        wind_speed_ms[start_blizzard:start_blizzard+duration] += np.random.normal(15, 2, duration)
    wind_speed_ms = np.clip(wind_speed_ms, 0, 40)
    
    # Solar irradiance (W/m^2)
    # Zero in winter, high in summer
    solar_declination = -23.44 * np.cos(2 * np.pi * (day_of_year + 10) / 365.25)
    latitude = -70.76 # Maitri station
    hour_angle = (time_index.hour.values - 12) * 15
    # Simplistic solar model
    irradiance = 1000 * np.clip(np.cos(np.radians(latitude - solar_declination)) * np.cos(np.radians(hour_angle)), 0, 1)
    
    # Polar night (roughly mid-May to mid-July)
    irradiance[ambient_temp_c < -35] *= 0.5 # Just some correlation for cloudy days
    irradiance = np.clip(irradiance, 0, 1200)

    # Station load (kW)
    # Base load + winter heating (depends on temp) + daily pattern + noise
    base_load = 50 
    heating_load = np.maximum(0, -10 - ambient_temp_c) * 2 
    daily_pattern = 20 * np.sin(np.pi * (time_index.hour.values - 6) / 12) * (time_index.hour.values >= 6) * (time_index.hour.values <= 18)
    noise_load = np.random.normal(0, 5, hours)
    load_kw = np.clip(base_load + heating_load + daily_pattern + noise_load, 20, 200)
    
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from simulator.equipment import SolarPanel, WindTurbine
    
    solar_panel = SolarPanel()
    wind_turbine = WindTurbine()
    
    solar_kw = solar_panel.get_power(irradiance)
    wind_kw = wind_turbine.get_power(wind_speed_ms, ambient_temp_c)

    df = pd.DataFrame({
        "time": time_index,
        "ambient_temp_c": ambient_temp_c,
        "wind_speed_ms": wind_speed_ms,
        "solar_irradiance": irradiance,
        "solar_kw": solar_kw,
        "wind_kw": wind_kw,
        "load_kw": load_kw
    })
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {hours} hours of data to {output_path}")
    return df

if __name__ == "__main__":
    generate_year_data("backend/data/station_year.csv")
