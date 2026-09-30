import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
import joblib
import os
import sys

def create_features(df):
    """Create lag features, time features and weather features."""
    df = df.copy()
    
    # Time features
    df['hour'] = df['time'].dt.hour
    df['dayofweek'] = df['time'].dt.dayofweek
    df['dayofyear'] = df['time'].dt.dayofyear
    df['month'] = df['time'].dt.month
    
    # Lag features (past 24h, 48h)
    for col in ['load_kw', 'solar_kw', 'wind_kw']:
        df[f'{col}_lag24'] = df[col].shift(24)
        df[f'{col}_lag48'] = df[col].shift(48)
        
    df = df.dropna().reset_index(drop=True)
    return df

def train_and_evaluate(df, target_col, features, model_path):
    print(f"\n--- Training {target_col} ---")
    
    # Split: first 10 months (until roughly Nov 1) vs last 2 months
    # 8760 hours -> 10 months is roughly 7300 hours
    # Using actual datetime for split
    split_date = df['time'].min() + pd.DateOffset(months=10)
    
    train_df = df[df['time'] < split_date]
    test_df = df[df['time'] >= split_date]
    
    X_train = train_df[features]
    y_train = train_df[target_col]
    X_test = test_df[features]
    y_test = test_df[target_col]
    
    model = lgb.LGBMRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    preds = np.maximum(preds, 0) # Ensure non-negative
    
    # Evaluation
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mape = mean_absolute_percentage_error(y_test + 1e-5, preds)
    
    # Baseline: same time yesterday (lag24)
    baseline_preds = test_df[f'{target_col}_lag24']
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_preds))
    baseline_mape = mean_absolute_percentage_error(y_test + 1e-5, baseline_preds)
    
    print(f"Model RMSE: {rmse:.2f}, MAPE: {mape:.2%}")
    print(f"Baseline RMSE: {baseline_rmse:.2f}, MAPE: {baseline_mape:.2%}")
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Saved model to {model_path}")
    return model

def main():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "station_year.csv")
    if not os.path.exists(data_path):
        print(f"Data not found at {data_path}. Generate data first.")
        return
        
    df = pd.read_csv(data_path, parse_dates=['time'])
    df = create_features(df)
    
    # Common features
    base_features = ['hour', 'dayofweek', 'dayofyear', 'month']
    
    # Load model
    load_features = base_features + ['ambient_temp_c', 'wind_speed_ms', 'load_kw_lag24', 'load_kw_lag48']
    train_and_evaluate(df, 'load_kw', load_features, "backend/ml/load_model.pkl")
    
    # Solar model
    solar_features = base_features + ['solar_irradiance', 'solar_kw_lag24', 'solar_kw_lag48']
    train_and_evaluate(df, 'solar_kw', solar_features, "backend/ml/solar_model.pkl")
    
    # Wind model
    wind_features = base_features + ['wind_speed_ms', 'ambient_temp_c', 'wind_kw_lag24', 'wind_kw_lag48']
    train_and_evaluate(df, 'wind_kw', wind_features, "backend/ml/wind_model.pkl")

if __name__ == "__main__":
    main()
