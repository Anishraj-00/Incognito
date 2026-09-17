import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from backend.schemas.prediction import ForecastResponse, PredictionRequest
from backend.schemas.segment import SegmentListResponse, SegmentStatus
from backend.schemas.analytics import LocationAnalysisSchema, SystemAnalyticsResponse
from backend.services.prediction_service import PredictionService
from backend.services.congestion_service import CongestionService
from backend.services.analytics_service import AnalyticsService


def create_test_app() -> FastAPI:
    """
    Creates a FastAPI test instance wiring the Developer 3 services to API endpoints.
    This serves as both contract verification and the reference wiring for Developer 2.
    """
    app = FastAPI(title="TrafficAI Test API")

    @app.get("/api/segments", response_model=SegmentListResponse)
    def list_segments():
        return CongestionService.get_all_segments()

    @app.get("/api/segments/{location_id}", response_model=SegmentStatus)
    def get_segment(location_id: str):
        segment = CongestionService.get_segment_by_id(location_id)
        if not segment:
            raise HTTPException(status_code=404, detail=f"Segment '{location_id}' not found")
        return segment

    @app.get("/api/prediction/{location_id}", response_model=ForecastResponse)
    def get_prediction(location_id: str, horizon: int = 3):
        try:
            return PredictionService.forecast(location_id, horizon=horizon)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/api/prediction/forecast", response_model=ForecastResponse)
    def post_prediction(request: PredictionRequest):
        try:
            return PredictionService.forecast(request.location_id, horizon=request.horizon)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.get("/api/analytics/{location_id}", response_model=LocationAnalysisSchema)
    def get_analytics(location_id: str):
        try:
            return AnalyticsService.get_location_analytics(location_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.get("/api/analytics/system/summary", response_model=SystemAnalyticsResponse)
    def get_system_summary():
        return AnalyticsService.get_system_overview()

    return app


@pytest.fixture(scope="module")
def client():
    app = create_test_app()
    with TestClient(app) as test_client:
        yield test_client


def test_api_list_segments(client):
    """Verify GET /api/segments endpoint returns valid list of road segments."""
    response = client.get("/api/segments")
    assert response.status_code == 200
    data = response.json()
    assert "total_segments" in data
    assert "segments" in data
    assert data["total_segments"] > 0
    assert len(data["segments"]) == data["total_segments"]


def test_api_get_segment_by_id(client):
    """Verify GET /api/segments/{location_id} returns correct segment details."""
    response = client.get("/api/segments/LOC_A")
    assert response.status_code == 200
    data = response.json()
    assert data["location_id"] == "LOC_A"
    assert "Downtown" in data["name"]
    assert data["congestion_level"] in ["LOW", "MEDIUM", "HIGH"]

    # 404 for invalid segment
    notFound = client.get("/api/segments/NON_EXISTENT")
    assert notFound.status_code == 404


def test_api_get_prediction(client):
    """Verify GET /api/prediction/{location_id} generates valid forecast."""
    response = client.get("/api/prediction/LOC_A?horizon=2")
    assert response.status_code == 200
    data = response.json()
    assert data["location_id"] == "LOC_A"
    assert data["horizon"] == 2
    assert len(data["forecasts"]) == 2
    for forecast in data["forecasts"]:
        assert forecast["predicted_traffic"] >= 0
        assert 0.0 <= forecast["confidence"] <= 100.0
        assert 0.0 <= forecast["congestion_index"] <= 1.0


def test_api_post_prediction(client):
    """Verify POST /api/prediction/forecast accepts JSON body and returns forecast."""
    payload = {"location_id": "LOC_B", "horizon": 3}
    response = client.post("/api/prediction/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["location_id"] == "LOC_B"
    assert len(data["forecasts"]) == 3


def test_api_prediction_validation_error(client):
    """Verify invalid horizon triggers 422 Unprocessable Entity."""
    response = client.post("/api/prediction/forecast", json={"location_id": "LOC_A", "horizon": 50})
    assert response.status_code == 422


def test_api_location_analytics(client):
    """Verify GET /api/analytics/{location_id} returns location metrics."""
    response = client.get("/api/analytics/LOC_A")
    assert response.status_code == 200
    data = response.json()
    assert data["location"] == "LOC_A"
    assert data["historical_average_volume"] > 0
    assert "peak_hours" in data


def test_api_system_summary(client):
    """Verify GET /api/analytics/system/summary returns system overview."""
    response = client.get("/api/analytics/system/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_locations"] >= 3
    assert data["global_average_volume"] > 0
