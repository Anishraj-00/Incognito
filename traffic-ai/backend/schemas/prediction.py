from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class PredictionRequest(BaseModel):
    location_id: str = Field(..., description="The ID of the location/intersection", example="Jubilee Hills")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current time")
    volume: Optional[int] = Field(None, description="Current vehicle count", example=125)
    speed: Optional[float] = Field(None, description="Average speed in km/h", example=24.5)

class PredictionResponse(BaseModel):
    location: str
    timestamp: str
    predicted_traffic: Optional[int] = None
    congestion_level: Optional[str] = None
    congestion_index: Optional[float] = None
    confidence: Optional[float] = None
    uncertainty: Optional[float] = None
    explanation: Optional[List[str]] = None
    status: str = "model_unavailable"

class PredictionItem(BaseModel):
    pass

class ForecastResponse(BaseModel):
    pass

