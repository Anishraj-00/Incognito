from typing import List, Optional
from pydantic import BaseModel, Field


class PeakHoursSchema(BaseModel):
    location: str = Field(..., description="Location identifier or 'ALL'", example="LOC_A")
    morning_peak: Optional[str] = Field(None, description="Identified morning peak hour (e.g., '8:00')", example="8:00")
    evening_peak: Optional[str] = Field(None, description="Identified evening peak hour (e.g., '17:00')", example="17:00")
    highest_traffic_hour: Optional[str] = Field(None, description="Hour with the highest overall volume", example="17:00")
    peak_traffic_volume: Optional[float] = Field(None, description="Average volume during the peak traffic hour", example=520.4)


class LocationAnalysisSchema(BaseModel):
    location: str = Field(..., description="Location identifier", example="LOC_A")
    name: Optional[str] = Field(None, description="Friendly road name", example="Downtown Core Corridor")
    historical_average_volume: float = Field(..., description="Mean historical traffic volume", example=215.3)
    latest_volume: float = Field(..., description="Most recent traffic volume reading", example=310.0)
    latest_congestion_level: str = Field(..., description="Current congestion level: LOW, MEDIUM, or HIGH", example="HIGH")
    latest_timestamp: str = Field(..., description="Timestamp of the latest measurement")
    peak_hours: PeakHoursSchema = Field(..., description="Peak hours analysis breakdown")


class SystemAnalyticsResponse(BaseModel):
    total_locations: int = Field(..., description="Number of analyzed road segments")
    global_average_volume: float = Field(..., description="System-wide average hourly traffic volume")
    most_congested_location: Optional[str] = Field(None, description="Location currently experiencing highest congestion")
    locations: List[LocationAnalysisSchema] = Field(..., description="Detailed analytics per location")
