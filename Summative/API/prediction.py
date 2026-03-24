from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(
    title="🌾 Rwanda Crop Yield Prediction API",
    description="Predicts crop yield (kg/hectare) for small farmers in Rwanda.",
    version="1.0.0",
)

# Load model and scaler
model = joblib.load('best_model.pkl')
scaler = joblib.load('scaler.pkl')

class PredictionInput(BaseModel):
    Soil_Quality: float
    Seed_Variety: int
    Fertilizer_Amount_kg_per_hectare: float
    Sunny_Days: float
    Rainfall_mm: float
    Irrigation_Schedule: int

@app.post("/predict")
def predict(data: PredictionInput):
    # Create DataFrame from input
    df = pd.DataFrame([data.dict()])
    
    # Scale features
    df_scaled = scaler.transform(df)
    
    # Predict
    prediction = model.predict(df_scaled)
    
    return {
        "predicted_yield_kg_per_hectare": round(float(prediction[0]), 2),
        "unit": "kg/hectare"
    }
