from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np

# Load saved files
model = joblib.load("best_model.pkl")
scaler = joblib.load("scaler.pkl")
feature_columns = joblib.load("feature_columns.pkl")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Input Schema (dynamic)
# -----------------------------
class PredictionInput(BaseModel):
    data: dict  # flexible input

# -----------------------------
# Home route
# -----------------------------
@app.get("/")
def home():
    return {"message": "ML API is running successfully"}

# -----------------------------
# Predict Endpoint
# -----------------------------
@app.post("/predict")
def predict(input_data: PredictionInput):
    
    # Convert input dict → ordered list
    values = [input_data.data[col] for col in feature_columns]
    
    # Convert to numpy array
    data_array = np.array([values])
    
    # Scale
    data_scaled = scaler.transform(data_array)
    
    # Predict
    prediction = model.predict(data_scaled)
    
    return {
        "prediction": prediction.tolist()
    }

# -----------------------------
# Retrain Endpoint
# -----------------------------
@app.post("/retrain")
def retrain():
    return {"message": "Retraining endpoint ready (implement if needed)"}