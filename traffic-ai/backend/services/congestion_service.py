from typing import Optional, List
import pandas as pd

from backend.schemas.segment import SegmentStatus, SegmentListResponse
from backend.services.data_manager import get_traffic_data, SEGMENT_METADATA
from ml.congestion import classify_congestion, calculate_congestion_index


class CongestionService:
    @staticmethod
    def get_all_segments() -> SegmentListResponse:
        """
        Calculates and returns the latest congestion status for all monitored road segments.
        """
        df = get_traffic_data()
        classified_df = classify_congestion(df.copy())

        segments: List[SegmentStatus] = []
        low_count = 0
        med_count = 0
        high_count = 0

        # Group by location and get the latest observation per location
        for loc_id, group in classified_df.groupby("location_id"):
            latest_row = group.sort_values("timestamp").iloc[-1]
            metadata = SEGMENT_METADATA.get(loc_id, {
                "name": f"Road Segment {loc_id}",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "free_flow_speed": 60.0
            })

            status = SegmentStatus(
                location_id=str(loc_id),
                name=metadata["name"],
                latitude=metadata["latitude"],
                longitude=metadata["longitude"],
                current_volume=int(latest_row["volume"]),
                historical_average=float(group["volume"].mean()),
                congestion_level=str(latest_row.get("congestion_level", "UNKNOWN")),
                congestion_index=round(float(latest_row.get("congestion_index", 0.0)), 2),
                speed=round(float(latest_row.get("speed", metadata["free_flow_speed"])), 1),
                last_updated=str(latest_row["timestamp"])
            )
            segments.append(status)

            if status.congestion_level == "LOW":
                low_count += 1
            elif status.congestion_level == "MEDIUM":
                med_count += 1
            elif status.congestion_level == "HIGH":
                high_count += 1

        return SegmentListResponse(
            total_segments=len(segments),
            low_congestion_count=low_count,
            medium_congestion_count=med_count,
            high_congestion_count=high_count,
            segments=segments
        )

    @staticmethod
    def get_segment_by_id(location_id: str) -> Optional[SegmentStatus]:
        """
        Returns the latest congestion status for a specific road segment.
        """
        all_segments = CongestionService.get_all_segments()
        for seg in all_segments.segments:
            if seg.location_id == location_id:
                return seg
        return None
