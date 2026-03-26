from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np

app = FastAPI(
    title="🌾 Rwanda Crop Yield Prediction API",
    description="Predicts crop yield (kg/hectare) for small farmers in Rwanda.",
    version="1.0.0",
)

# Load model and scaler
model = joblib.load('best_model.pkl')
scaler = joblib.load('scaler.pkl')

class YieldInput(BaseModel):
    model_config = {"populate_by_name": True}

    soil_quality: float = Field(
        ..., alias="soil_quality", ge=50.0, le=100.0,
        description="Soil quality score (50–100)"
    )
    seed_variety: int = Field(
        ..., alias="seed_variety", ge=0, le=1,
        description="Seed variety: 0 = traditional, 1 = improved"
    )
    fertilizer_kg_per_ha: float = Field(
        ..., alias="fertilizer_kg_per_ha", ge=0.0, le=300.0,
        description="Fertilizer applied in kg/hectare (0–300)"
    )
    sunny_days: float = Field(
        ..., alias="sunny_days", ge=0.0, le=365.0,
        description="Number of sunny days (0–365)"
    )
    rainfall_mm: float = Field(
        ..., alias="rainfall_mm", ge=0.0, le=3000.0,
        description="Total rainfall in mm (0–3000)"
    )
    irrigation_schedule: int = Field(
        ..., alias="irrigation_schedule", ge=0, le=15,
        description="Irrigation frequency score (0–15)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "soil_quality": 78.5,
                "seed_variety": 1,
                "fertilizer_kg_per_ha": 120.0,
                "sunny_days": 180.0,
                "rainfall_mm": 950.0,
                "irrigation_schedule": 5,
            }
        }

@app.post("/predict")
def predict(data: YieldInput):
    # Transform input fields to array format
    features = np.array([[
        data.soil_quality,
        data.seed_variety,
        data.fertilizer_kg_per_ha,
        data.sunny_days,
        data.rainfall_mm,
        data.irrigation_schedule,
    ]])
    
    # Scale features
    df_scaled = scaler.transform(features)
    
    # Predict
    prediction = model.predict(df_scaled)
    
    return {
        "predicted_yield_kg_per_hectare": round(float(prediction[0]), 2),
        "unit": "kg/hectare"
    }
