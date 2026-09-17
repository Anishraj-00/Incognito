from fastapi import APIRouter, HTTPException
from backend.services.congestion_service import CongestionService
from backend.schemas.segment import SegmentListResponse, SegmentStatus

router = APIRouter(prefix="/congestion", tags=["Congestion"])


@router.get("", response_model=SegmentListResponse, summary="Get congestion status for all segments")
def get_congestion_overview():
    """
    Returns the latest real-time congestion status across all monitored road segments.

    Includes per-segment congestion level (LOW / MEDIUM / HIGH), congestion index,
    current volume, speed, and summary counts by severity.
    """
    try:
        return CongestionService.get_all_segments()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{location_id}", response_model=SegmentStatus, summary="Get congestion status for a specific segment")
def get_congestion_by_location(location_id: str):
    """
    Returns the latest real-time congestion status for a single road segment.

    - **location_id**: e.g. `LOC_A`, `LOC_B`, `LOC_C`

    Returns 404 if the location ID is not tracked.
    """
    try:
        segment = CongestionService.get_segment_by_id(location_id)
        if not segment:
            raise HTTPException(
                status_code=404,
                detail=f"Location '{location_id}' not found. Valid IDs are: LOC_A, LOC_B, LOC_C"
            )
        return segment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
