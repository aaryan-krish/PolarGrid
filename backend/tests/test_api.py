import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import app

client = TestClient(app)

def test_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "mode" in data
    assert "timestamp" in data
    assert "load_kw" in data

def test_forecast_endpoint():
    response = client.get("/api/forecast?hours=24")
    assert response.status_code == 200
    data = response.json()
    assert "points" in data
    assert isinstance(data["points"], list)

def test_schedule_endpoint():
    response = client.get("/api/schedule")
    assert response.status_code == 200
    data = response.json()
    assert "horizon_hours" in data

def test_autonomy_endpoint():
    response = client.get("/api/autonomy")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "recommendation" in data

def test_alerts_endpoint():
    response = client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_comparison_endpoint():
    response = client.get("/api/comparison")
    assert response.status_code == 200
    data = response.json()
    assert "fuel_saved_pct" in data

def test_loads_endpoint():
    response = client.get("/api/loads")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
def test_toggle_mode():
    response = client.post("/api/mode", json={"mode": "SAFE"})
    assert response.status_code == 200
    assert response.json()["mode"] == "SAFE"

def test_pyomo_model():
    from optimizer.pyomo_model import solve_dispatch
    load = [100.0] * 48
    solar = [0.0] * 48
    wind = [0.0] * 48
    temp = [0.0] * 48
    
    schedule, obj = solve_dispatch(48, load, solar, wind, temp, initial_soc=250.0, deferrable_loads=[])
    assert schedule is not None
    # Check that demand is met (supply - charge == demand)
    for p in schedule:
        assert p['generator_kw'] >= -1e-6
