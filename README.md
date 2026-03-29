#  Rwanda Crop Yield Prediction

## Mission
Help small farmers in Rwanda thrive by predicting crop yield (kg/hectare) based on soil quality, rainfall, fertilizer use, sunlight, seed variety, and irrigation inputs — enabling smarter farming decisions.

## Dataset
Agricultural Yield Prediction Dataset from Kaggle — 20,000 records with features: Soil_Quality, Seed_Variety, Fertilizer_Amount_kg_per_hectare, Sunny_Days, Rainfall_mm, Irrigation_Schedule. Target: Yield_kg_per_hectare.

## Public API
- **Base URL:** https://rwanda-yield-api.onrender.com
- **Swagger UI:** https://rwanda-yield-api.onrender.com/docs

## How to Run the Flutter App
1. Make sure Flutter is installed on your machine
2. Navigate into the FlutterApp folder: `cd summative/FlutterApp`
3. Run `flutter pub get` to install dependencies
4. Run `flutter run` to launch the app on your device or emulator

## Video Demo
[Link to YouTube video demo]

## Project Structure
```
linear_regression_model/
└── summative/
    ├── linear_regression/
    │   └── multivariate.ipynb
    ├── API/
    │   ├── prediction.py
    │   └── requirements.txt
    └── FlutterApp/
```
