import pandas as pd
import json
from ml.preprocess import preprocess_data
from ml.analytics import get_location_analysis, get_peak_hours
from ml.predict import forecast_traffic

def run_demo():
    print("Loading data for demo...")
    df = preprocess_data("data/raw/synthetic_traffic.csv")
    
    test_location = "LOC_A"
    print(f"\n--- Location Analysis for {test_location} ---")
    analysis = get_location_analysis(df, test_location)
    print(json.dumps(analysis, indent=2))
    
    print(f"\n--- 3-Hour Forecast for {test_location} ---")
    # Take the last 10 hours for feature engineering context
    recent_data = df[df['location_id'] == test_location].tail(10)
    
    forecasts = forecast_traffic(test_location, recent_data, horizon=3)
    
    for i, f in enumerate(forecasts):
        print(f"\nForecast +{i+1} hour ({f['timestamp']}):")
        print(f"  Traffic: {f['predicted_traffic']}")
        print(f"  Congestion: {f['congestion_level']} (Index: {f['congestion_index']:.2f})")
        print(f"  Confidence: {f['confidence']:.1f}%")
        print(f"  Explanation: {f['explanation'][0]}")

if __name__ == "__main__":
    run_demo()
