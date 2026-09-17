import pandas as pd
import numpy as np

def calculate_congestion_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates a congestion index (0 to 1) based on volume vs historical average.
    If speed is available, it factors into the index.
    """
    if 'loc_hist_avg' not in df.columns:
        # Fallback if features weren't generated
        df['loc_hist_avg'] = df.groupby('location_id')['volume'].transform('mean')
        
    # Baseline index based on volume relative to historical average
    # Index > 1 means above average traffic
    volume_ratio = df['volume'] / (df['loc_hist_avg'] + 1e-5)
    
    # Normalize to roughly 0-1 (we cap it later)
    # A ratio of 1.5 might mean quite congested. 
    base_index = (volume_ratio - 0.5) / 1.5 
    
    if 'speed' in df.columns:
        # Assuming speed < 20 is very congested, > 50 is free flow
        speed_factor = 1.0 - ((df['speed'] - 10) / 40.0)
        speed_factor = np.clip(speed_factor, 0, 1)
        # Combine volume and speed
        index = 0.6 * base_index + 0.4 * speed_factor
    else:
        index = base_index
        
    df['congestion_index'] = np.clip(index, 0, 1)
    return df

def classify_congestion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classifies congestion_index into LOW, MEDIUM, HIGH.
    """
    if 'congestion_index' not in df.columns:
        df = calculate_congestion_index(df)
        
    conditions = [
        (df['congestion_index'] < 0.4),
        (df['congestion_index'] >= 0.4) & (df['congestion_index'] < 0.7),
        (df['congestion_index'] >= 0.7)
    ]
    choices = ['LOW', 'MEDIUM', 'HIGH']
    
    df['congestion_level'] = np.select(conditions, choices, default='UNKNOWN')
    return df
