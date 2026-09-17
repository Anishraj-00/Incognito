from fastapi import APIRouter, HTTPException
from backend.services.congestion_service import CongestionService
from backend.schemas.segment import SegmentListResponse, SegmentStatus

router = APIRouter(prefix="/segments", tags=["Segments"])

@router.get("", response_model=SegmentListResponse)
def get_segments():
    """
    Returns latest congestion status for all monitored road segments.
    """
    try:
        return CongestionService.get_all_segments()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{segment_id}", response_model=SegmentStatus)
def get_segment(segment_id: str):
    """
    Returns the latest congestion status for a specific road segment.
    """
    try:
        segment = CongestionService.get_segment_by_id(segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail=f"Segment {segment_id} not found")
        return segment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
