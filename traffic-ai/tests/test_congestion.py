import pytest
import pandas as pd
import numpy as np

from backend.schemas.segment import SegmentStatus, SegmentListResponse
from backend.services.congestion_service import CongestionService
from backend.services.analytics_service import AnalyticsService
from ml.congestion import calculate_congestion_index, classify_congestion


def test_calculate_congestion_index():
    """Verify congestion index calculation formula and bounds."""
    df = pd.DataFrame({
        "location_id": ["LOC_A", "LOC_A"],
        "volume": [100, 300],
        "loc_hist_avg": [200.0, 200.0],
        "speed": [55.0, 20.0]
    })
    result = calculate_congestion_index(df)
    assert "congestion_index" in result.columns
    # Congestion index should be within [0, 1]
    assert (result["congestion_index"] >= 0.0).all()
    assert (result["congestion_index"] <= 1.0).all()
    # Higher volume and lower speed should have higher congestion index
    assert result["congestion_index"].iloc[1] > result["congestion_index"].iloc[0]


def test_classify_congestion_thresholds():
    """Verify LOW, MEDIUM, HIGH thresholds."""
    df = pd.DataFrame({
        "congestion_index": [0.2, 0.5, 0.85]
    })
    result = classify_congestion(df)
    assert result["congestion_level"].iloc[0] == "LOW"
    assert result["congestion_level"].iloc[1] == "MEDIUM"
    assert result["congestion_level"].iloc[2] == "HIGH"


def test_get_all_segments():
    """Verify CongestionService aggregates all monitored segments correctly."""
    response = CongestionService.get_all_segments()
    assert isinstance(response, SegmentListResponse)
    assert response.total_segments > 0
    assert len(response.segments) == response.total_segments

    # Check sum of category counts
    sum_counts = (
        response.low_congestion_count
        + response.medium_congestion_count
        + response.high_congestion_count
    )
    assert sum_counts == response.total_segments

    # Check metadata enrichment
    for seg in response.segments:
        assert isinstance(seg.name, str)
        assert len(seg.name) > 0
        assert seg.latitude != 0.0
        assert seg.longitude != 0.0
        assert seg.congestion_level in ["LOW", "MEDIUM", "HIGH"]
        assert 0.0 <= seg.congestion_index <= 1.0


def test_get_segment_by_id():
    """Test retrieving single segment by ID."""
    segment = CongestionService.get_segment_by_id("LOC_A")
    assert segment is not None
    assert segment.location_id == "LOC_A"
    assert "Downtown" in segment.name

    # Non-existent segment should return None
    missing = CongestionService.get_segment_by_id("UNKNOWN_LOC")
    assert missing is None


def test_analytics_service_peak_hours():
    """Verify peak hours calculations."""
    peak_info = AnalyticsService.get_peak_hours(location_id="LOC_A")
    assert peak_info.location == "LOC_A"
    assert peak_info.morning_peak is not None
    assert peak_info.evening_peak is not None


def test_analytics_service_location_summary():
    """Verify full location analysis."""
    analysis = AnalyticsService.get_location_analytics(location_id="LOC_A")
    assert analysis.location == "LOC_A"
    assert analysis.historical_average_volume > 0
    assert analysis.latest_congestion_level in ["LOW", "MEDIUM", "HIGH"]
    assert analysis.peak_hours is not None


def test_analytics_service_system_overview():
    """Verify system-wide analytics summary."""
    overview = AnalyticsService.get_system_overview()
    assert overview.total_locations >= 3
    assert overview.global_average_volume > 0
    assert len(overview.locations) == overview.total_locations
