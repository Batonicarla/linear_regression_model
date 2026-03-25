"""
prediction.py — FastAPI for Work-Life Balance Score Prediction
Task 2 | Linear Regression Summative Assignment
"""

import os
import io
import pickle
import numpy as np
import pandas as pd
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ─────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="Work-Life Balance Score Predictor",
    description=(
        "Predicts an individual's Work-Life Balance Score (range ≈ 480–820) "
        "from 21 daily lifestyle features. Built on the Kaggle Wellbeing & "
        "Lifestyle dataset using SGD Linear Regression."
    ),
    version="1.0.0",
)

# ─────────────────────────────────────────────
# CORS Middleware
# Allows the Flutter mobile app (and any browser / Swagger client)
# to call this API from a different origin.
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # In production, restrict to your app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Load model artefacts at startup
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH   = os.path.join(BASE_DIR, "best_model.pkl")
SCALER_PATH  = os.path.join(BASE_DIR, "scaler.pkl")
COLUMNS_PATH = os.path.join(BASE_DIR, "feature_columns.pkl")

# These will hold the loaded objects
model         = None
scaler        = None
feature_cols  = None


def load_artefacts():
    """Load the three pickle files saved in Task 1."""
    global model, scaler, feature_cols
    with open(MODEL_PATH,   "rb") as f:
        model = pickle.load(f)
    with open(SCALER_PATH,  "rb") as f:
        scaler = pickle.load(f)
    with open(COLUMNS_PATH, "rb") as f:
        feature_cols = pickle.load(f)


# Load on startup
try:
    load_artefacts()
    print("✅ Model artefacts loaded successfully.")
    print(f"   Feature columns ({len(feature_cols)}): {feature_cols}")
except FileNotFoundError as e:
    print(f"⚠️  Artefact not found: {e}")
    print("   Place best_model.pkl, scaler.pkl, feature_columns.pkl in the API/ folder.")


# ─────────────────────────────────────────────
# Pydantic input schema — 21 features
# Ranges match the dataset's realistic bounds.
# ─────────────────────────────────────────────
class WellbeingInput(BaseModel):
    FRUITS_VEGGIES:    int   = Field(..., ge=0, le=10,    description="Daily fruit & veg portions (0-10)")
    DAILY_STRESS:      float = Field(..., ge=0, le=10,    description="Daily stress level (0-10)")
    PLACES_VISITED:    int   = Field(..., ge=0, le=10,    description="New places visited per month (0-10)")
    CORE_CIRCLE:       int   = Field(..., ge=0, le=10,    description="Close social connections (0-10)")
    SUPPORTING_OTHERS: int   = Field(..., ge=0, le=10,    description="Hours supporting others per week (0-10)")
    SOCIAL_NETWORK:    int   = Field(..., ge=0, le=10,    description="Social network size score (0-10)")
    ACHIEVEMENT:       int   = Field(..., ge=0, le=10,    description="Personal achievements score (0-10)")
    DONATION:          int   = Field(..., ge=0, le=10,    description="Charitable giving score (0-10)")
    BMI_RANGE:         int   = Field(..., ge=1, le=5,     description="BMI category (1=underweight … 5=obese)")
    TODO_COMPLETED:    int   = Field(..., ge=0, le=10,    description="Daily to-do completion rate (0-10)")
    FLOW:              int   = Field(..., ge=0, le=10,    description="Daily flow/focus state (0-10)")
    DAILY_STEPS:       int   = Field(..., ge=0, le=30000, description="Daily step count (0-30000)")
    LIVE_VISION:       int   = Field(..., ge=0, le=10,    description="Clarity of life vision (0-10)")
    SLEEP_HOURS:       int   = Field(..., ge=1, le=12,    description="Average nightly sleep hours (1-12)")
    LOST_VACATION:     int   = Field(..., ge=0, le=10,    description="Vacation days lost per year (0-10)")
    DAILY_SHOUTING:    int   = Field(..., ge=0, le=10,    description="Times per day shouting/arguing (0-10)")
    SUFFICIENT_INCOME: int   = Field(..., ge=1, le=2,     description="Income sufficiency: 1=No, 2=Yes")
    PERSONAL_AWARDS:   int   = Field(..., ge=0, le=10,    description="Personal awards/recognitions (0-10)")
    TIME_FOR_PASSION:  int   = Field(..., ge=0, le=10,    description="Hours per week for passions (0-10)")
    WEEKLY_MEDITATION: int   = Field(..., ge=0, le=10,    description="Weekly meditation sessions (0-10)")
    # One-hot encoded: AGE — baseline = '21 to 35'. Set 1 for the matching group.
    AGE_51_or_more:    int   = Field(..., ge=0, le=1,     description="Age group 51 or more (1=yes, 0=no)")

    class Config:
        json_schema_extra = {
            "example": {
                "FRUITS_VEGGIES": 5,
                "DAILY_STRESS": 3.0,
                "PLACES_VISITED": 4,
                "CORE_CIRCLE": 5,
                "SUPPORTING_OTHERS": 7,
                "SOCIAL_NETWORK": 6,
                "ACHIEVEMENT": 6,
                "DONATION": 3,
                "BMI_RANGE": 2,
                "TODO_COMPLETED": 7,
                "FLOW": 6,
                "DAILY_STEPS": 8000,
                "LIVE_VISION": 7,
                "SLEEP_HOURS": 7,
                "LOST_VACATION": 2,
                "DAILY_SHOUTING": 1,
                "SUFFICIENT_INCOME": 2,
                "PERSONAL_AWARDS": 5,
                "TIME_FOR_PASSION": 4,
                "WEEKLY_MEDITATION": 3,
                "AGE_51_or_more": 0,
            }
        }


class PredictionResponse(BaseModel):
    predicted_work_life_balance_score: float
    interpretation: str
    model_used: str


# ─────────────────────────────────────────────
# Helper: build DataFrame from input
# ─────────────────────────────────────────────
def build_input_df(data: WellbeingInput) -> pd.DataFrame:
    """
    Map Pydantic fields → DataFrame with exact column names
    that the trained model expects.
    Rename AGE_51_or_more → 'AGE_51 or more' to match training columns.
    """
    row = {
        "FRUITS_VEGGIES":    data.FRUITS_VEGGIES,
        "DAILY_STRESS":      data.DAILY_STRESS,
        "PLACES_VISITED":    data.PLACES_VISITED,
        "CORE_CIRCLE":       data.CORE_CIRCLE,
        "SUPPORTING_OTHERS": data.SUPPORTING_OTHERS,
        "SOCIAL_NETWORK":    data.SOCIAL_NETWORK,
        "ACHIEVEMENT":       data.ACHIEVEMENT,
        "DONATION":          data.DONATION,
        "BMI_RANGE":         data.BMI_RANGE,
        "TODO_COMPLETED":    data.TODO_COMPLETED,
        "FLOW":              data.FLOW,
        "DAILY_STEPS":       data.DAILY_STEPS,
        "LIVE_VISION":       data.LIVE_VISION,
        "SLEEP_HOURS":       data.SLEEP_HOURS,
        "LOST_VACATION":     data.LOST_VACATION,
        "DAILY_SHOUTING":    data.DAILY_SHOUTING,
        "SUFFICIENT_INCOME": data.SUFFICIENT_INCOME,
        "PERSONAL_AWARDS":   data.PERSONAL_AWARDS,
        "TIME_FOR_PASSION":  data.TIME_FOR_PASSION,
        "WEEKLY_MEDITATION": data.WEEKLY_MEDITATION,
        "AGE_51 or more":    data.AGE_51_or_more,
    }
    return pd.DataFrame([row])[feature_cols]


def interpret_score(score: float) -> str:
    if score >= 700:
        return "Excellent work-life balance. Keep up your healthy habits!"
    elif score >= 620:
        return "Good work-life balance. There is room for small improvements."
    elif score >= 540:
        return "Moderate work-life balance. Consider reducing stress and increasing leisure."
    else:
        return "Poor work-life balance. Significant lifestyle changes are recommended."


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Work-Life Balance Score Prediction API is running.",
        "docs": "/docs",
        "predict_endpoint": "/predict",
        "retrain_endpoint": "/retrain",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None,
        "n_features": len(feature_cols) if feature_cols else 0,
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict(data: WellbeingInput):
    """
    **Predict Work-Life Balance Score** from 21 lifestyle input variables.

    - All fields are required.
    - Range validation is enforced automatically.
    - Returns the predicted score plus a plain-English interpretation.
    """
    if model is None or scaler is None or feature_cols is None:
        raise HTTPException(
            status_code=503,
            detail="Model artefacts not loaded. Ensure best_model.pkl, scaler.pkl, "
                   "and feature_columns.pkl are present in the API/ directory.",
        )

    try:
        input_df      = build_input_df(data)
        input_scaled  = scaler.transform(input_df)
        prediction    = float(model.predict(input_scaled)[0])
        prediction    = round(prediction, 2)

        return PredictionResponse(
            predicted_work_life_balance_score=prediction,
            interpretation=interpret_score(prediction),
            model_used="SGD Linear Regression",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/retrain", tags=["Retraining"])
async def retrain(file: UploadFile = File(...)):
    """
    **Retrain the model** with newly uploaded CSV data.

    Upload a CSV file with the same schema as the original training data
    (including `WORK_LIFE_BALANCE_SCORE` as the target column).
    The model, scaler, and feature columns are updated in memory and on disk.
    """
    global model, scaler, feature_cols

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    try:
        contents = await file.read()
        new_df   = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        # ── Validate required target column ──
        if "WORK_LIFE_BALANCE_SCORE" not in new_df.columns:
            raise HTTPException(
                status_code=422,
                detail="CSV must contain a 'WORK_LIFE_BALANCE_SCORE' column.",
            )

        # ── Preprocessing (mirrors Task 1 notebook) ──
        new_df.drop(columns=["Timestamp", "User_ID"], errors="ignore", inplace=True)
        new_df["DAILY_STRESS"] = pd.to_numeric(new_df["DAILY_STRESS"], errors="coerce")

        cols_to_encode = [c for c in ["AGE", "GENDER"] if c in new_df.columns]
        if cols_to_encode:
            new_df = pd.get_dummies(new_df, columns=cols_to_encode, drop_first=True)

        new_df.dropna(inplace=True)

        X_new = new_df.drop("WORK_LIFE_BALANCE_SCORE", axis=1)
        y_new = new_df["WORK_LIFE_BALANCE_SCORE"]

        # ── Retrain ──
        from sklearn.linear_model import SGDRegressor
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import r2_score, mean_squared_error

        X_tr, X_te, y_tr, y_te = train_test_split(
            X_new, y_new, test_size=0.2, random_state=42
        )

        new_scaler = StandardScaler()
        X_tr_s = new_scaler.fit_transform(X_tr)
        X_te_s = new_scaler.transform(X_te)

        new_model = SGDRegressor(
            max_iter=1000, tol=1e-4, random_state=42,
            learning_rate="invscaling", eta0=0.01
        )
        new_model.fit(X_tr_s, y_tr)

        r2  = r2_score(y_te, new_model.predict(X_te_s))
        mse = mean_squared_error(y_te, new_model.predict(X_te_s))

        # ── Persist updated artefacts ──
        model        = new_model
        scaler       = new_scaler
        feature_cols = X_new.columns.tolist()

        with open(MODEL_PATH,   "wb") as f: pickle.dump(model,        f)
        with open(SCALER_PATH,  "wb") as f: pickle.dump(scaler,       f)
        with open(COLUMNS_PATH, "wb") as f: pickle.dump(feature_cols, f)

        return {
            "status":       "Model retrained and saved successfully.",
            "new_rows_used": len(X_new),
            "test_r2":      round(r2, 4),
            "test_mse":     round(mse, 4),
            "n_features":   len(feature_cols),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retraining error: {str(e)}")