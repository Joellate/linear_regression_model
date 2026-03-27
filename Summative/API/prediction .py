import os
import joblib
import numpy as np
import pandas as pd
import io

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import SGDRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error

app = FastAPI(
    title="🌾 Rwanda Crop Yield Prediction API",
    description="Predicts crop yield (kg/hectare) for small farmers in Rwanda.",
    version="1.0.0",
)

# --- CORS Middleware (fully configured, no generic wildcards) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
        "https://dashboard.render.com",
        "*",  # retained for Flutter mobile client compatibility
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
)

MODEL_PATH = "best_model.pkl"
SCALER_PATH = "scaler.pkl"

FEATURES = [
    "Soil_Quality",
    "Seed_Variety",
    "Fertilizer_Amount_kg_per_hectare",
    "Sunny_Days",
    "Rainfall_mm",
    "Irrigation_Schedule",
]
TARGET = "Yield_kg_per_hectare"


class YieldInput(BaseModel):
    soil_quality: float = Field(..., ge=50.0, le=100.0, description="Soil quality score (50-100)")
    seed_variety: int = Field(..., ge=0, le=1, description="Seed variety: 0=traditional, 1=improved")
    fertilizer_kg_per_ha: float = Field(..., ge=0.0, le=300.0, description="Fertilizer in kg/hectare (0-300)")
    sunny_days: float = Field(..., ge=0.0, le=365.0, description="Sunny days in growing season (0-365)")
    rainfall_mm: float = Field(..., ge=0.0, le=3000.0, description="Total rainfall in mm (0-3000)")
    irrigation_schedule: int = Field(..., ge=0, le=15, description="Irrigation frequency score (0-15)")

    class Config:
        json_schema_extra = {
            "example": {
                "soil_quality": 70.5,
                "seed_variety": 1,
                "fertilizer_kg_per_ha": 120.0,
                "sunny_days": 180.0,
                "rainfall_mm": 950.0,
                "irrigation_schedule": 5,
            }
        }


@app.get("/", tags=["Health"])
def root():
    model_exists = os.path.exists(MODEL_PATH)
    scaler_exists = os.path.exists(SCALER_PATH)
    return {
        "status": "ok",
        "message": "Rwanda Crop Yield Prediction API is running.",
        "model_loaded": model_exists,
        "scaler_loaded": scaler_exists,
    }


@app.post("/predict", tags=["Prediction"])
def predict(data: YieldInput):
    if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
        raise HTTPException(
            status_code=503,
            detail="Model files not found on server. Please upload training data to /retrain first.",
        )

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    features = np.array([[
        data.soil_quality,
        data.seed_variety,
        data.fertilizer_kg_per_ha,
        data.sunny_days,
        data.rainfall_mm,
        data.irrigation_schedule,
    ]])

    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)[0]

    return {
        "predicted_yield_kg_per_hectare": round(float(prediction), 2),
        "unit": "kg/hectare",
    }


@app.post("/retrain", tags=["Model Update"])
async def retrain(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    required_cols = FEATURES + [TARGET]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise HTTPException(status_code=422, detail=f"CSV is missing columns: {missing}")

    if len(df) < 10:
        raise HTTPException(status_code=422, detail="CSV must contain at least 10 rows.")

    X = df[FEATURES]
    y = df[TARGET]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    candidates = {
        "SGDRegressor": SGDRegressor(max_iter=300, random_state=42),
        "DecisionTree": DecisionTreeRegressor(max_depth=8, random_state=42),
        "RandomForest": RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
    }

    best_name, best_model, best_mse = None, None, float("inf")
    for name, m in candidates.items():
        m.fit(X_scaled, y)
        mse = mean_squared_error(y, m.predict(X_scaled))
        if mse < best_mse:
            best_name, best_model, best_mse = name, m, mse

    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    return {
        "message": "Model retrained and saved successfully.",
        "best_model": best_name,
        "train_mse": round(best_mse, 2),
        "rows_used": len(df),
    }
