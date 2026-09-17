import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_synthetic_traffic_data(output_path="data/raw/synthetic_traffic.csv", num_days=90):
    """
    Generates synthetic traffic data for hackathon development.
    DO NOT PRETEND THIS IS REAL WORLD DATA.
    This simulates traffic volume for a few locations over a period of time,
    incorporating day-of-week, hour-of-day, and random weather effects.
    """
    np.random.seed(42)
    
    locations = ["LOC_A", "LOC_B", "LOC_C"]
    
    start_date = datetime.now() - timedelta(days=num_days)
    end_date = datetime.now()
    
    # Generate hourly timestamps
    timestamps = pd.date_range(start=start_date, end=end_date, freq='h')
    
    data = []
    
    for loc in locations:
        # Base traffic for location
        base_traffic = np.random.randint(100, 300)
        
        for ts in timestamps:
            hour = ts.hour
            day_of_week = ts.dayofweek
            is_weekend = day_of_week >= 5
            
            # Morning peak (7-9 AM) and Evening peak (16-18 PM) multipliers
            time_multiplier = 1.0
            if 7 <= hour <= 9 and not is_weekend:
                time_multiplier = 2.5
            elif 16 <= hour <= 18 and not is_weekend:
                time_multiplier = 2.8
            elif 10 <= hour <= 15:
                time_multiplier = 1.5
            elif hour < 6 or hour > 22:
                time_multiplier = 0.3
                
            if is_weekend:
                if 10 <= hour <= 18:
                    time_multiplier = 1.6
                else:
                    time_multiplier *= 0.5
            
            # Random weather effects
            rainfall = np.random.choice([0, 0, 0, 5, 10, 20], p=[0.7, 0.1, 0.1, 0.05, 0.03, 0.02])
            temperature = 20 + np.random.normal(0, 5) - (rainfall * 0.5)
            
            # Traffic is reduced slightly by heavy rain, but congestion might increase
            weather_multiplier = 1.0 if rainfall < 10 else 0.9
            
            noise = np.random.normal(0, 0.1)
            
            volume = int(base_traffic * time_multiplier * weather_multiplier * (1 + noise))
            
            # Speed is inversely related to volume roughly
            free_flow_speed = 60 if loc == "LOC_A" else 45
            speed = max(5, free_flow_speed - (volume / 20) + np.random.normal(0, 5))
            
            data.append({
                "timestamp": ts,
                "location_id": loc,
                "volume": max(0, volume),
                "speed": speed,
                "rainfall": rainfall,
                "temperature": temperature
            })
            
    df = pd.DataFrame(data)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Synthetic data generated at {output_path} with {len(df)} records.")
    return df

if __name__ == "__main__":
    generate_synthetic_traffic_data()
