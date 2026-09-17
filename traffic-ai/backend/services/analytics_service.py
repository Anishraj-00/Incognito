from typing import Optional, List
import pandas as pd

from backend.schemas.analytics import (
    PeakHoursSchema,
    LocationAnalysisSchema,
    SystemAnalyticsResponse,
)
from backend.services.data_manager import get_traffic_data, SEGMENT_METADATA
from ml.analytics import get_location_analysis, get_peak_hours
from ml.congestion import classify_congestion


class AnalyticsService:
    @staticmethod
    def get_peak_hours(location_id: Optional[str] = None) -> PeakHoursSchema:
        """
        Calculates peak morning, evening, and highest traffic hours.
        """
        df = get_traffic_data()
        raw_peaks = get_peak_hours(df, location=location_id)
        return PeakHoursSchema(
            location=raw_peaks.get("location", location_id or "ALL"),
            morning_peak=raw_peaks.get("morning_peak"),
            evening_peak=raw_peaks.get("evening_peak"),
            highest_traffic_hour=raw_peaks.get("highest_traffic_hour"),
            peak_traffic_volume=raw_peaks.get("peak_traffic_volume")
        )

    @staticmethod
    def get_location_analytics(location_id: str) -> LocationAnalysisSchema:
        """
        Returns full analytics breakdown for a single road segment.
        """
        df = get_traffic_data()
        df = classify_congestion(df)
        raw_analysis = get_location_analysis(df, location_id)

        if "error" in raw_analysis:
            valid_locs = sorted(df["location_id"].unique().tolist())
            raise ValueError(f"Location '{location_id}' not found. Valid locations: {valid_locs}")

        raw_peaks = raw_analysis.get("peak_hours", {})
        peak_hours_obj = PeakHoursSchema(
            location=location_id,
            morning_peak=raw_peaks.get("morning_peak"),
            evening_peak=raw_peaks.get("evening_peak"),
            highest_traffic_hour=raw_peaks.get("highest_traffic_hour"),
            peak_traffic_volume=raw_peaks.get("peak_traffic_volume")
        )

        metadata = SEGMENT_METADATA.get(location_id, {})
        friendly_name = metadata.get("name", f"Segment {location_id}")

        return LocationAnalysisSchema(
            location=raw_analysis["location"],
            name=friendly_name,
            historical_average_volume=round(raw_analysis["historical_average_volume"], 2),
            latest_volume=float(raw_analysis["latest_volume"]),
            latest_congestion_level=str(raw_analysis["latest_congestion_level"]),
            latest_timestamp=str(raw_analysis["latest_timestamp"]),
            peak_hours=peak_hours_obj
        )

    @staticmethod
    def get_system_overview() -> SystemAnalyticsResponse:
        """
        Aggregates analytics across all monitored locations.
        """
        df = get_traffic_data()
        locations = sorted(df["location_id"].unique().tolist())

        location_analyses: List[LocationAnalysisSchema] = []
        highest_volume = -1.0
        busiest_location = None

        for loc in locations:
            analysis = AnalyticsService.get_location_analytics(loc)
            location_analyses.append(analysis)
            if analysis.latest_volume > highest_volume:
                highest_volume = analysis.latest_volume
                busiest_location = loc

        global_avg = round(float(df["volume"].mean()), 2)

        return SystemAnalyticsResponse(
            total_locations=len(location_analyses),
            global_average_volume=global_avg,
            most_congested_location=busiest_location,
            locations=location_analyses
        )
