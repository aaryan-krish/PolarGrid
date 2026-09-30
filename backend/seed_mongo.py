import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI or "<username>" in MONGODB_URI:
    print("❌ Please set your actual MONGODB_URI in the backend/.env file first!")
    exit(1)

print("Connecting to MongoDB...")
client = MongoClient(MONGODB_URI)
db = client.polargrid_database

print("Clearing old telemetry data...")
db.telemetry.delete_many({})

print("Generating fake historical data...")
fake_data = []
now = datetime.utcnow()

# Generate 50 hours of fake historical data
for i in range(50, 0, -1):
    record_time = now - timedelta(hours=i)
    
    # Simulate some realistic fluctuating values
    is_blizzard = random.random() > 0.9
    wind_speed = random.uniform(25, 35) if is_blizzard else random.uniform(5, 15)
    solar = 0 if is_blizzard else random.uniform(0, 40)
    
    doc = {
        "timestamp": record_time.isoformat(),
        "mode": "AI",
        "load_kw": random.uniform(50, 80),
        "solar_kw": solar,
        "wind_kw": wind_speed * 1.5,
        "generator_kw": random.choice([0, 0, 50]), # Mostly off, sometimes on
        "generator_on": False,
        "battery_soc_pct": random.uniform(40, 95),
        "battery_kw": random.uniform(-20, 20),
        "battery_temp_c": random.uniform(-15, -5),
        "fuel_litres": 10000 - (50 - i) * 10, # Slowly decreasing
        "ambient_temp_c": random.uniform(-30, -10),
        "wind_speed_ms": wind_speed,
        "blizzard_mode": is_blizzard
    }
    
    # Fix generator boolean
    doc["generator_on"] = doc["generator_kw"] > 0
    
    fake_data.append(doc)

print(f"Uploading {len(fake_data)} records to MongoDB...")
result = db.telemetry.insert_many(fake_data)

print(f"✅ Successfully uploaded {len(result.inserted_ids)} records!")
print("You can now view this data in MongoDB Atlas under 'Browse Collections'.")
