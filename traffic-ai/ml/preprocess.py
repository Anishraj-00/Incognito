import pandas as pd
import numpy as np
import os

def load_data(file_path: str) -> pd.DataFrame:
    """Loads raw traffic data from a CSV file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    return pd.read_csv(file_path)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the dataset by handling missing values and duplicates."""
    # Drop duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    if 'speed' in df.columns:
        df['speed'] = df['speed'].fillna(df['speed'].median())
    if 'volume' in df.columns:
        df['volume'] = df['volume'].fillna(df['volume'].median())
    
    # Fill remaining with forward fill then backward fill
    df = df.ffill().bfill()
    
    return df

def validate_data(df: pd.DataFrame) -> bool:
    """Validates the presence of required columns."""
    required_columns = ['timestamp', 'location_id', 'volume']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    return True

def preprocess_data(file_path: str) -> pd.DataFrame:
    """End-to-end preprocessing pipeline."""
    df = load_data(file_path)
    validate_data(df)
    
    # Parse timestamps
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort chronologically
    df = df.sort_values(by=['location_id', 'timestamp']).reset_index(drop=True)
    
    df = clean_data(df)
    
    return df
