import joblib
import pandas as pd
import numpy as np
import os

class Forecaster:
    def __init__(self, model_dir="backend/ml"):
        self.load_model = joblib.load(os.path.join(model_dir, "load_model.pkl"))
        self.solar_model = joblib.load(os.path.join(model_dir, "solar_model.pkl"))
        self.wind_model = joblib.load(os.path.join(model_dir, "wind_model.pkl"))

    def predict(self, current_time, past_data: pd.DataFrame, future_weather: pd.DataFrame, hours: int = 48):
        """
        past_data should contain the last 48 hours of data (at least).
        future_weather should contain ambient_temp_c, wind_speed_ms, solar_irradiance for the next `hours`.
        """
        # Create a dataframe for the next `hours`
        times = pd.date_range(current_time + pd.Timedelta(hours=1), periods=hours, freq='h')
        
        df = pd.DataFrame({'time': times})
        df['hour'] = df['time'].dt.hour
        df['dayofweek'] = df['time'].dt.dayofweek
        df['dayofyear'] = df['time'].dt.dayofyear
        df['month'] = df['time'].dt.month
        
        # Attach future weather
        df['ambient_temp_c'] = future_weather['ambient_temp_c'].values[:hours]
        df['wind_speed_ms'] = future_weather['wind_speed_ms'].values[:hours]
        df['solar_irradiance'] = future_weather['solar_irradiance'].values[:hours]
        
        # We will predict step by step to use our own predictions as lags, or just use the naive lags.
        # Given lag24/48, for a 48h horizon, the first 24h will partly use true data, partly predictions.
        
        predictions = {
            'load_kw': [],
            'solar_kw': [],
            'wind_kw': []
        }
        
        # Keep track of the series for lags
        hist = past_data.copy()
        
        for i in range(hours):
            current_row = df.iloc[i:i+1].copy()
            
            # Extract lags from hist
            for col in ['load_kw', 'solar_kw', 'wind_kw']:
                current_row[f'{col}_lag24'] = hist[col].iloc[-24]
                current_row[f'{col}_lag48'] = hist[col].iloc[-48]
                
            # Predict
            pred_load = self.load_model.predict(current_row[['hour', 'dayofweek', 'dayofyear', 'month', 'ambient_temp_c', 'wind_speed_ms', 'load_kw_lag24', 'load_kw_lag48']])[0]
            pred_solar = self.solar_model.predict(current_row[['hour', 'dayofweek', 'dayofyear', 'month', 'solar_irradiance', 'solar_kw_lag24', 'solar_kw_lag48']])[0]
            pred_wind = self.wind_model.predict(current_row[['hour', 'dayofweek', 'dayofyear', 'month', 'wind_speed_ms', 'ambient_temp_c', 'wind_kw_lag24', 'wind_kw_lag48']])[0]
            
            pred_load = max(0, pred_load)
            pred_solar = max(0, pred_solar)
            pred_wind = max(0, pred_wind)
            
            predictions['load_kw'].append(pred_load)
            predictions['solar_kw'].append(pred_solar)
            predictions['wind_kw'].append(pred_wind)
            
            # Append to hist for future lags
            new_row = pd.DataFrame({
                'load_kw': [pred_load],
                'solar_kw': [pred_solar],
                'wind_kw': [pred_wind]
            })
            hist = pd.concat([hist, new_row], ignore_index=True)
            
        df['load_kw'] = predictions['load_kw']
        df['solar_kw'] = predictions['solar_kw']
        df['wind_kw'] = predictions['wind_kw']
        
        return df[['time', 'load_kw', 'solar_kw', 'wind_kw', 'ambient_temp_c', 'wind_speed_ms']]
