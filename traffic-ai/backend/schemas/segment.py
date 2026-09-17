from typing import List, Optional
from pydantic import BaseModel, Field


class SegmentLocation(BaseModel):
    location_id: str = Field(..., description="Unique identifier for the road segment", example="LOC_A")
    name: str = Field(..., description="Descriptive human-readable name of the road segment", example="Downtown Core Corridor")
    latitude: float = Field(..., description="Latitude coordinate", example=37.7749)
    longitude: float = Field(..., description="Longitude coordinate", example=-122.4194)
    free_flow_speed: float = Field(default=60.0, description="Expected free flow speed limit in km/h", example=60.0)


class SegmentStatus(BaseModel):
    location_id: str = Field(..., description="Unique segment identifier", example="LOC_A")
    name: str = Field(..., description="Road segment name", example="Downtown Core Corridor")
    latitude: float = Field(..., description="Latitude coordinate", example=37.7749)
    longitude: float = Field(..., description="Longitude coordinate", example=-122.4194)
    current_volume: int = Field(..., ge=0, description="Latest vehicle volume count", example=245)
    historical_average: float = Field(..., ge=0.0, description="Baseline historical average volume for this segment", example=180.5)
    congestion_level: str = Field(..., description="Congestion classification: LOW, MEDIUM, or HIGH", example="HIGH")
    congestion_index: float = Field(..., ge=0.0, le=1.0, description="Normalized congestion index (0.0 - 1.0)", example=0.82)
    speed: float = Field(..., ge=0.0, description="Latest estimated average speed (km/h)", example=24.5)
    last_updated: str = Field(..., description="Timestamp of the latest reading")


class SegmentListResponse(BaseModel):
    total_segments: int = Field(..., description="Total count of monitored road segments")
    low_congestion_count: int = Field(default=0, description="Segments currently at LOW congestion")
    medium_congestion_count: int = Field(default=0, description="Segments currently at MEDIUM congestion")
    high_congestion_count: int = Field(default=0, description="Segments currently at HIGH congestion")
    segments: List[SegmentStatus] = Field(..., description="List of monitored road segments with current statuses")
