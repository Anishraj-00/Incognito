import pandas as pd

def get_peak_hours(df: pd.DataFrame, location: str = None) -> dict:
    """Identifies peak hours for a location or globally from historical data."""
    if location:
        df = df[df['location_id'] == location]
        
    if df.empty:
        return {}
        
    # Group by hour and day_of_week
    hourly = df.groupby(['is_weekend', 'hour'])['volume'].mean().reset_index()
    
    # Weekday peaks
    weekday = hourly[hourly['is_weekend'] == 0]
    
    if not weekday.empty:
        # Morning peak (e.g. 6-11)
        morning_mask = (weekday['hour'] >= 6) & (weekday['hour'] <= 11)
        morning_peak = weekday[morning_mask].loc[weekday[morning_mask]['volume'].idxmax()] if not weekday[morning_mask].empty else None
        
        # Evening peak (e.g. 15-20)
        evening_mask = (weekday['hour'] >= 15) & (weekday['hour'] <= 20)
        evening_peak = weekday[evening_mask].loc[weekday[evening_mask]['volume'].idxmax()] if not weekday[evening_mask].empty else None
        
        highest_hour = weekday.loc[weekday['volume'].idxmax()]
    else:
        morning_peak = evening_peak = highest_hour = None
        
    res = {
        "location": location if location else "ALL",
        "morning_peak": f"{int(morning_peak['hour'])}:00" if morning_peak is not None else None,
        "evening_peak": f"{int(evening_peak['hour'])}:00" if evening_peak is not None else None,
        "highest_traffic_hour": f"{int(highest_hour['hour'])}:00" if highest_hour is not None else None,
        "peak_traffic_volume": float(highest_hour['volume']) if highest_hour is not None else None
    }
    return res

def get_location_analysis(df: pd.DataFrame, location: str) -> dict:
    """Provides a summary analysis for a specific location."""
    loc_data = df[df['location_id'] == location]
    if loc_data.empty:
        return {"error": "Location not found"}
        
    latest = loc_data.iloc[-1]
    
    avg_vol = loc_data['volume'].mean()
    
    return {
        "location": location,
        "historical_average_volume": float(avg_vol),
        "latest_volume": float(latest['volume']),
        "latest_congestion_level": latest.get('congestion_level', 'UNKNOWN'),
        "latest_timestamp": str(latest['timestamp']),
        "peak_hours": get_peak_hours(loc_data)
    }
