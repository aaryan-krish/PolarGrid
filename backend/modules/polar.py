import numpy as np

def calculate_autonomy(fuel_litres, avg_daily_burn_l, days_to_resupply):
    days_remaining = fuel_litres / avg_daily_burn_l if avg_daily_burn_l > 0 else 999
    
    if days_remaining < days_to_resupply * 1.1:
        status = "CRITICAL"
        rec = "Implement severe load shedding. Critical loads only."
    elif days_remaining < days_to_resupply * 1.5:
        status = "WARNING"
        rec = "Conserve fuel. Defer non-essential loads."
    else:
        status = "OK"
        rec = "Fuel levels adequate."
        
    return {
        "fuel_litres": fuel_litres,
        "avg_daily_burn_l": avg_daily_burn_l,
        "days_remaining": days_remaining,
        "days_to_resupply": days_to_resupply,
        "status": status,
        "recommendation": rec
    }

def check_blizzard(wind_forecast, threshold=20.0):
    """
    If wind exceeds threshold in the next 24h, trigger blizzard mode.
    Blizzard mode should force the optimizer to pre-charge the battery (by adding a penalty or constraint).
    Here we just detect it for the API.
    """
    if any(w > threshold for w in wind_forecast[:24]):
        return True
    return False

from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.01, random_state=42)
        self.is_trained = False
        
    def train(self, historical_fuel, historical_load):
        if len(historical_fuel) < 100:
            return
        X = np.column_stack([historical_load, historical_fuel])
        self.model.fit(X)
        self.is_trained = True
        
    def check_anomaly(self, current_load, current_fuel):
        if not self.is_trained:
            return False
        X = np.array([[current_load, current_fuel]])
        pred = self.model.predict(X)
        return pred[0] == -1
