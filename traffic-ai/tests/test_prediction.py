import pytest
from pydantic import ValidationError
from backend.schemas.prediction import PredictionRequest, PredictionItem, ForecastResponse
from backend.services.prediction_service import PredictionService


def test_prediction_request_schema():
    """Verify PredictionRequest validates horizon boundaries."""
    req = PredictionRequest(location_id="LOC_A", horizon=3)
    assert req.location_id == "LOC_A"
    assert req.horizon == 3

    # Invalid horizon < 1
    with pytest.raises(ValidationError):
        PredictionRequest(location_id="LOC_A", horizon=0)

    # Invalid horizon > 24
    with pytest.raises(ValidationError):
        PredictionRequest(location_id="LOC_A", horizon=25)


def test_prediction_item_schema():
    """Verify PredictionItem constraints."""
    item = PredictionItem(
        location="LOC_A",
        timestamp="2026-09-17T12:00:00",
        predicted_traffic=150,
        congestion_level="MEDIUM",
        congestion_index=0.55,
        confidence=88.5,
        uncertainty=12.3,
        explanation=["Traffic peak period"]
    )
    assert item.predicted_traffic == 150
    assert 0.0 <= item.congestion_index <= 1.0
    assert 0.0 <= item.confidence <= 100.0


def test_supported_locations():
    """Verify supported locations include LOC_A, LOC_B, LOC_C."""
    locations = PredictionService.get_supported_locations()
    assert isinstance(locations, list)
    assert "LOC_A" in locations
    assert "LOC_B" in locations
    assert "LOC_C" in locations


def test_forecast_horizon_1():
    """Test 1-hour forecast execution and schema compliance."""
    response = PredictionService.forecast(location_id="LOC_A", horizon=1)
    assert isinstance(response, ForecastResponse)
    assert response.location_id == "LOC_A"
    assert response.horizon == 1
    assert len(response.forecasts) == 1

    first = response.forecasts[0]
    assert first.predicted_traffic >= 0
    assert first.congestion_level in ["LOW", "MEDIUM", "HIGH"]
    assert 0.0 <= first.congestion_index <= 1.0
    assert 0.0 <= first.confidence <= 100.0
    assert isinstance(first.explanation, list)
    assert len(first.explanation) > 0


def test_forecast_multi_step():
    """Test multi-hour recursive forecast execution."""
    horizon = 3
    response = PredictionService.forecast(location_id="LOC_B", horizon=horizon)
    assert response.horizon == horizon
    assert len(response.forecasts) == horizon

    # Ensure timestamps advance
    timestamps = [f.timestamp for f in response.forecasts]
    assert len(set(timestamps)) == horizon


def test_forecast_invalid_location():
    """Test that requesting an invalid location raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        PredictionService.forecast(location_id="NON_EXISTENT_LOC", horizon=1)


def test_forecast_invalid_horizon():
    """Test that invalid horizon raises ValueError."""
    with pytest.raises(ValueError):
        PredictionService.forecast(location_id="LOC_A", horizon=0)
    with pytest.raises(ValueError):
        PredictionService.forecast(location_id="LOC_A", horizon=30)
