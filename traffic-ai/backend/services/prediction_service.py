"""
Prediction Service — connects the FastAPI prediction route to the ML inference layer.
Implements PredictionService with multi-step recursive forecasting via ml/predict.py.
"""

from typing import List
import logging

from backend.schemas.prediction import ForecastResponse, PredictionItem
from backend.services.data_manager import get_traffic_data, get_model_artifacts, SEGMENT_METADATA

logger = logging.getLogger(__name__)

# Valid locations supported by the system
SUPPORTED_LOCATIONS: List[str] = list(SEGMENT_METADATA.keys())


class PredictionService:
    """Service layer for traffic congestion forecasting."""

    @staticmethod
    def get_supported_locations() -> List[str]:
        """Return the list of location IDs supported by the trained model."""
        return SUPPORTED_LOCATIONS

    @staticmethod
    def forecast(location_id: str, horizon: int = 3) -> ForecastResponse:
        """
        Generate a multi-step recursive traffic forecast for a given location.

        Args:
            location_id: One of the monitored segment IDs (e.g. 'LOC_A').
            horizon: Number of 1-hour steps to forecast (1–24).

        Returns:
            ForecastResponse with an ordered list of PredictionItem objects.

        Raises:
            ValueError: If location_id is unknown or horizon is out of range.
        """
        if horizon < 1 or horizon > 24:
            raise ValueError(f"horizon must be between 1 and 24, got {horizon}")

        if location_id not in SUPPORTED_LOCATIONS:
            raise ValueError(
                f"Location '{location_id}' not found. "
                f"Valid locations: {SUPPORTED_LOCATIONS}"
            )

        # Load data and model (cached after first call)
        df = get_traffic_data()
        _artifacts = get_model_artifacts()  # ensures model is ready; used inside ml.predict

        try:
            from ml.predict import forecast_traffic
            raw_forecasts = forecast_traffic(
                location=location_id,
                current_data=df,
                horizon=horizon,
            )
        except Exception as exc:
            logger.exception("ML forecast failed for %s — falling back to heuristic", location_id)
            raw_forecasts = _heuristic_forecast(location_id, df, horizon)

        items: List[PredictionItem] = []
        for raw in raw_forecasts:
            confidence = float(raw.get("confidence", 75.0))
            # ml/confidence.py may return values in 0–1 range; normalise to 0–100
            if confidence <= 1.0:
                confidence = round(confidence * 100, 2)
            confidence = max(0.0, min(100.0, confidence))

            congestion_index = float(raw.get("congestion_index", 0.5))
            congestion_index = max(0.0, min(1.0, congestion_index))

            items.append(
                PredictionItem(
                    location=str(raw.get("location", location_id)),
                    timestamp=str(raw.get("timestamp", "")),
                    predicted_traffic=max(0, int(raw.get("predicted_traffic", 0))),
                    congestion_level=str(raw.get("congestion_level", "MEDIUM")),
                    congestion_index=round(congestion_index, 4),
                    confidence=round(confidence, 2),
                    uncertainty=round(float(raw.get("uncertainty", 5.0)), 2),
                    explanation=list(raw.get("explanation", [])),
                )
            )

        return ForecastResponse(
            location_id=location_id,
            horizon=horizon,
            forecasts=items,
        )


# ---------------------------------------------------------------------------
# Internal heuristic fallback (mirrors ml/generate_data.py peak-hour logic)
# Used when the trained model file is not yet present at demo startup.
# ---------------------------------------------------------------------------

def _heuristic_forecast(location_id: str, df, horizon: int) -> list:
    """
    Simple rule-based fallback forecast.  Runs without a trained model so the
    API never returns a 500 at hackathon demo time.
    """
    import pandas as pd
    from datetime import datetime, timedelta

    loc_df = df[df["location_id"] == location_id]
    if loc_df.empty:
        base_vol = 200
        last_ts = datetime.utcnow()
    else:
        base_vol = int(loc_df["volume"].mean())
        try:
            last_ts = pd.to_datetime(loc_df["timestamp"].max())
        except Exception:
            last_ts = datetime.utcnow()

    results = []
    for i in range(horizon):
        next_ts = last_ts + timedelta(hours=i + 1)
        hour = next_ts.hour
        is_weekend = next_ts.weekday() >= 5

        if 7 <= hour <= 9 and not is_weekend:
            mult = 2.45
        elif 16 <= hour <= 18 and not is_weekend:
            mult = 2.75
        elif 10 <= hour <= 15:
            mult = 1.45
        elif hour < 6 or hour > 22:
            mult = 0.35
        else:
            mult = 1.10
        if is_weekend:
            mult = 1.55 if 11 <= hour <= 18 else mult * 0.65

        vol = max(20, int(base_vol * mult))
        hist_avg = base_vol * 1.35
        raw_idx = (vol / (hist_avg + 1e-5) - 0.5) / 1.5
        cong_idx = max(0.05, min(0.97, raw_idx))
        level = "LOW" if cong_idx < 0.40 else ("MEDIUM" if cong_idx < 0.70 else "HIGH")

        results.append({
            "location": location_id,
            "timestamp": next_ts.isoformat(),
            "predicted_traffic": vol,
            "congestion_level": level,
            "congestion_index": round(cong_idx, 4),
            "confidence": 72.0,
            "uncertainty": 8.0,
            "explanation": [
                "Heuristic fallback: ML model warming up.",
                f"{'Peak' if mult > 2.0 else 'Off-peak'} hour pattern applied.",
            ],
        })

    return results


# Convenience function alias kept for backwards compatibility with the route layer
def predict_congestion(request):
    """Single-step convenience wrapper used by the legacy /predict route."""
    response = PredictionService.forecast(
        location_id=request.location_id,
        horizon=1,
    )
    if not response.forecasts:
        from backend.schemas.prediction import PredictionResponse
        return PredictionResponse(
            location=request.location_id,
            timestamp=str(request.timestamp),
            status="no_data",
        )
    item = response.forecasts[0]
    from backend.schemas.prediction import PredictionResponse
    return PredictionResponse(
        location=item.location,
        timestamp=item.timestamp,
        predicted_traffic=item.predicted_traffic,
        congestion_level=item.congestion_level,
        congestion_index=item.congestion_index,
        confidence=item.confidence,
        uncertainty=item.uncertainty,
        explanation=item.explanation,
        status="ok",
    )
