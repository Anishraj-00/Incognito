from fastapi import APIRouter, HTTPException
from backend.schemas.prediction import PredictionRequest, PredictionResponse, ForecastResponse
from backend.services.prediction_service import predict_congestion, PredictionService
import logging

router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """
    Predict traffic congestion for a given location (single-step).
    Delegates to the ML service layer.
    """
    try:
        response = predict_congestion(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during prediction")


@router.get("/predict/{location_id}", response_model=ForecastResponse)
def get_forecast(location_id: str, horizon: int = 3):
    """
    Generate a multi-step forecast for a road segment.
    Query param: horizon (1-24, default 3).
    """
    try:
        return PredictionService.forecast(location_id=location_id, horizon=horizon)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Forecast error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during forecast")


@router.post("/predict/forecast", response_model=ForecastResponse)
def post_forecast(request: PredictionRequest):
    """
    POST endpoint for multi-step forecast. Accepts full PredictionRequest body.
    """
    try:
        return PredictionService.forecast(
            location_id=request.location_id,
            horizon=request.horizon,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Forecast error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during forecast")
