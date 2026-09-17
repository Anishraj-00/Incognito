from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class PredictionRequest(BaseModel):
    location_id: str = Field(
        ...,
        description="The ID of the road segment / location",
        example="LOC_A",
    )
    horizon: int = Field(
        default=3,
        ge=1,
        le=24,
        description="Number of hours to forecast ahead (1-24)",
        example=3,
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Reference timestamp for the forecast",
    )


class PredictionItem(BaseModel):
    location: str = Field(..., description="Location identifier", example="LOC_A")
    timestamp: str = Field(..., description="Forecast timestamp (ISO string)")
    predicted_traffic: int = Field(..., ge=0, description="Predicted vehicle volume (veh/hr)")
    congestion_level: str = Field(
        ..., description="Congestion classification: LOW, MEDIUM, or HIGH"
    )
    congestion_index: float = Field(
        ..., ge=0.0, le=1.0, description="Normalised congestion index (0.0–1.0)"
    )
    confidence: float = Field(
        ..., ge=0.0, le=100.0, description="Model prediction confidence (0–100%)"
    )
    uncertainty: float = Field(
        ..., ge=0.0, description="Prediction uncertainty / standard deviation"
    )
    explanation: List[str] = Field(
        default_factory=list, description="Human-readable explanation factors"
    )


class ForecastResponse(BaseModel):
    location_id: str = Field(..., description="Location identifier", example="LOC_A")
    horizon: int = Field(..., ge=1, le=24, description="Number of forecast steps")
    forecasts: List[PredictionItem] = Field(
        ..., description="Ordered list of per-hour predictions"
    )


# Legacy single-step response kept for backwards compatibility
class PredictionResponse(BaseModel):
    location: str
    timestamp: str
    predicted_traffic: Optional[int] = None
    congestion_level: Optional[str] = None
    congestion_index: Optional[float] = None
    confidence: Optional[float] = None
    uncertainty: Optional[float] = None
    explanation: Optional[List[str]] = None
    status: str = "ok"
