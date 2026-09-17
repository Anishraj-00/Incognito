from datetime import datetime
from typing import List
import pandas as pd

from backend.schemas.prediction import ForecastResponse, PredictionItem
from backend.services.data_manager import (
    MODEL_DIR,
    get_traffic_data,
    ensure_data_and_model_ready,
)
from ml.predict import forecast_traffic


class PredictionService:
    @staticmethod
    def get_supported_locations() -> List[str]:
        """Returns list of valid location IDs."""
        df = get_traffic_data()
        return sorted(df['location_id'].unique().tolist())

    @staticmethod
    def forecast(location_id: str, horizon: int = 3) -> ForecastResponse:
        """
        Generates step-by-step traffic volume and congestion forecast for given location.
        """
        if horizon < 1 or horizon > 24:
            raise ValueError("Forecast horizon must be between 1 and 24 hours.")

        ensure_data_and_model_ready()
        df = get_traffic_data()

        location_df = df[df['location_id'] == location_id]
        if location_df.empty:
            valid_locs = sorted(df['location_id'].unique().tolist())
            raise ValueError(f"Location '{location_id}' not found. Valid locations: {valid_locs}")

        # Fetch recent historical context (last 12 hours) required for rolling/lag features
        recent_data = location_df.tail(12).copy()

        # Run ML forecast inference
        raw_forecasts = forecast_traffic(
            location=location_id,
            current_data=recent_data,
            horizon=horizon,
            model_dir=str(MODEL_DIR)
        )

        prediction_items = [
            PredictionItem(
                location=item["location"],
                timestamp=str(item["timestamp"]),
                predicted_traffic=int(item["predicted_traffic"]),
                congestion_level=str(item["congestion_level"]),
                congestion_index=float(item["congestion_index"]),
                confidence=float(item["confidence"]),
                uncertainty=float(item["uncertainty"]),
                explanation=item.get("explanation", [])
            )
            for item in raw_forecasts
        ]

        return ForecastResponse(
            location_id=location_id,
            horizon=horizon,
            generated_at=datetime.utcnow().isoformat() + "Z",
            forecasts=prediction_items
        )
