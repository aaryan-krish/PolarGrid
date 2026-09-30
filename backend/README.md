# PolarGrid AI Backend

Backend for the PolarGrid AI smart energy management system.

## Setup

1. Create a virtual environment and install requirements:
```bash
py -3.11 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

2. Generate the synthetic data:
```bash
python simulator/generate_data.py
```

3. Train the forecasting models (LightGBM):
```bash
python ml/train_models.py
```

## Running the API

Run the FastAPI server with Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```

## Testing

Run the pytest suite:
```bash
pytest tests/
```
