from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any

class PredictionRequest(BaseModel):
    location_id: str = Field(..., description="The ID of the location/intersection", example="Jubilee Hills")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current time")
    volume: Optional[int] = Field(None, description="Current vehicle count", example=125)
    speed: Optional[float] = Field(None, description="Average speed in km/h", example=24.5)

class PredictionResponse(BaseModel):
    location: str
    timestamp: str
    predicted_traffic: int
    congestion_level: str
    congestion_index: float
    confidence: float
    uncertainty: float
    explanation: List[str]
    status: str = "success"
