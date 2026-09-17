from fastapi import APIRouter, HTTPException
from backend.services.analytics_service import AnalyticsService
from backend.schemas.analytics import SystemAnalyticsResponse, LocationAnalysisSchema

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary", response_model=SystemAnalyticsResponse)
def get_analytics_summary():
    """
    Returns system-wide traffic analytics overview.
    """
    try:
        return AnalyticsService.get_system_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/locations/{location_id}", response_model=LocationAnalysisSchema)
def get_location_analytics(location_id: str):
    """
    Returns analytics breakdown for a single road segment.
    """
    try:
        return AnalyticsService.get_location_analytics(location_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
