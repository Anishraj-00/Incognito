from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PredictionRequest(BaseModel):
    location_id: str = Field(..., description="Unique identifier of the road segment/location (e.g. LOC_A)", example="LOC_A")
    horizon: int = Field(default=3, ge=1, le=24, description="Forecast horizon in hours (between 1 and 24)", example=3)


class PredictionItem(BaseModel):
    location: str = Field(..., description="Location identifier")
    timestamp: str = Field(..., description="Forecasted timestamp in ISO format")
    predicted_traffic: int = Field(..., ge=0, description="Predicted vehicle count")
    congestion_level: str = Field(..., description="Congestion category: LOW, MEDIUM, HIGH")
    congestion_index: float = Field(..., ge=0.0, le=1.0, description="Normalized congestion score between 0.0 and 1.0")
    confidence: float = Field(..., ge=0.0, le=100.0, description="Model prediction confidence percentage (0-100%)")
    uncertainty: float = Field(..., ge=0.0, description="Model prediction standard deviation / uncertainty estimate")
    explanation: List[str] = Field(default_factory=list, description="Explanatory insights for this prediction")


class ForecastResponse(BaseModel):
    location_id: str = Field(..., description="Target location identifier")
    horizon: int = Field(..., description="Number of forecasted hours ahead")
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z", description="Timestamp when prediction was generated")
    forecasts: List[PredictionItem] = Field(..., description="Sequence of step-by-step forecasted traffic states")
