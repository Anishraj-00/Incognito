from fastapi import APIRouter, HTTPException
from backend.schemas.prediction import PredictionRequest, PredictionResponse
from backend.services.prediction_service import predict_congestion
import logging

router = APIRouter(tags=["Prediction"])

@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Predict traffic congestion for a given location.
    Delegates to the ML service layer.
    """
    try:
        response = predict_congestion(request)
        return response
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during prediction")
