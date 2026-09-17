import requests
import random
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

class TrafficAPIClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url

    def get_health(self):
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {"status": "offline (mock mode)"}

    def get_segments(self):
        try:
            response = requests.get(f"{self.base_url}/api/segments", timeout=2)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return self._generate_mock_segments()

    def get_analytics(self):
        try:
            response = requests.get(f"{self.base_url}/api/analytics", timeout=2)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return self._generate_mock_analytics()

    def get_predictions(self, location_id: str, horizon: int = 24):
        try:
            response = requests.get(f"{self.base_url}/api/predictions/{location_id}?horizon={horizon}", timeout=2)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return self._generate_mock_predictions(location_id, horizon)

    # --- MOCK DATA GENERATORS (FALLBACK) ---
    def _generate_mock_segments(self):
        locations = [
            {"id": "LOC_A", "name": "Downtown Core Corridor", "lat": 37.7749, "lon": -122.4194},
            {"id": "LOC_B", "name": "Highway 101 North", "lat": 37.7858, "lon": -122.4064},
            {"id": "LOC_C", "name": "Golden Gate Bridge Approach", "lat": 37.8079, "lon": -122.4735},
            {"id": "LOC_D", "name": "Market St Intersection", "lat": 37.7739, "lon": -122.4312},
        ]
        
        segments = []
        low_count, med_count, high_count = 0, 0, 0
        
        for loc in locations:
            idx = random.uniform(0.1, 0.9)
            if idx < 0.4:
                level = "LOW"
                low_count += 1
            elif idx < 0.7:
                level = "MEDIUM"
                med_count += 1
            else:
                level = "HIGH"
                high_count += 1
                
            segments.append({
                "location_id": loc["id"],
                "name": loc["name"],
                "latitude": loc["lat"],
                "longitude": loc["lon"],
                "current_volume": int(random.uniform(50, 500)),
                "historical_average": 200.0,
                "congestion_level": level,
                "congestion_index": round(idx, 2),
                "speed": round(random.uniform(15, 65), 1),
                "last_updated": datetime.utcnow().isoformat() + "Z"
            })
            
        return {
            "total_segments": len(locations),
            "low_congestion_count": low_count,
            "medium_congestion_count": med_count,
            "high_congestion_count": high_count,
            "segments": segments
        }

    def _generate_mock_analytics(self):
        return {
            "total_locations": 4,
            "global_average_volume": 250.5,
            "most_congested_location": "LOC_C",
            "locations": [
                {
                    "location": "LOC_C",
                    "name": "Golden Gate Bridge Approach",
                    "historical_average_volume": 220.0,
                    "latest_volume": 410.0,
                    "latest_congestion_level": "HIGH",
                    "latest_timestamp": datetime.utcnow().isoformat() + "Z",
                    "peak_hours": {
                        "location": "LOC_C",
                        "morning_peak": "08:00",
                        "evening_peak": "17:00",
                        "highest_traffic_hour": "17:00",
                        "peak_traffic_volume": 450.0
                    }
                }
            ]
        }

    def _generate_mock_predictions(self, location_id: str, horizon: int):
        forecasts = []
        base_time = datetime.utcnow()
        base_volume = random.randint(100, 300)
        
        for i in range(1, horizon + 1):
            target_time = base_time + timedelta(hours=i)
            # Add some sine wave seasonality
            volume = base_volume + int(50 * random.random() + 100 * (target_time.hour % 12) / 12.0)
            
            idx = min(volume / 500.0, 1.0)
            level = "HIGH" if idx > 0.7 else ("MEDIUM" if idx > 0.4 else "LOW")
            
            forecasts.append({
                "location": location_id,
                "timestamp": target_time.isoformat() + "Z",
                "predicted_traffic": volume,
                "congestion_level": level,
                "congestion_index": round(idx, 2),
                "confidence": round(random.uniform(70, 95), 1),
                "uncertainty": round(random.uniform(5, 20), 1),
                "explanation": ["Based on historical trends.", "Weather impact considered."]
            })
            
        return {
            "location_id": location_id,
            "horizon": horizon,
            "generated_at": base_time.isoformat() + "Z",
            "forecasts": forecasts
        }
