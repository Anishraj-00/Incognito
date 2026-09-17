import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from ml.preprocess import preprocess_data
from ml.features import engineer_features
from ml.congestion import classify_congestion

def temporal_train_test_split(df: pd.DataFrame, test_size=0.2):
    """Chronological split to prevent data leakage."""
    split_idx = int(len(df) * (1 - test_size))
    train = df.iloc[:split_idx].copy()
    test = df.iloc[split_idx:].copy()
    return train, test

def prepare_training_data(df: pd.DataFrame, target_col='volume'):
    """Prepares features and target for training. Target is next hour volume."""
    # Create target: t+1 volume
    df = df.sort_values(by=['location_id', 'timestamp'])
    df['target'] = df.groupby('location_id')[target_col].shift(-1)
    
    # Drop last row per location (missing target)
    df = df.dropna(subset=['target'])
    
    # Select features
    features = [
        'hour', 'day_of_week', 'is_weekend', 'is_morning_peak', 'is_evening_peak',
        'volume', 'lag_1', 'lag_2', 'lag_3', 'rolling_mean_3h', 'rolling_std_3h',
        'traffic_change', 'loc_hist_avg'
    ]
    
    # Add weather if available
    for col in ['rainfall', 'temperature']:
        if col in df.columns:
            features.append(col)
            
    # Location encoding (simple one-hot)
    df = pd.get_dummies(df, columns=['location_id'], drop_first=False)
    loc_cols = [c for c in df.columns if c.startswith('location_id_')]
    features.extend(loc_cols)
    
    return df, features, 'target'

def train_model(data_path="data/raw/synthetic_traffic.csv", model_dir="models"):
    print("Loading and preprocessing data...")
    df = preprocess_data(data_path)
    
    print("Engineering features...")
    df = engineer_features(df)
    df = classify_congestion(df)
    
    # Save the feature columns and location averages for prediction
    loc_avgs = df[['location_id', 'loc_hist_avg']].drop_duplicates().set_index('location_id')['loc_hist_avg'].to_dict()
    
    # Prepare data
    df_prep, feature_cols, target_col = prepare_training_data(df)
    
    # Split
    print("Splitting data chronologically...")
    train, test = temporal_train_test_split(df_prep, test_size=0.2)
    
    X_train, y_train = train[feature_cols], train[target_col]
    X_test, y_test = test[feature_cols], test[target_col]
    
    print(f"Training Random Forest on {len(X_train)} samples...")
    # Use reasonable defaults for speed
    model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    print("Evaluating...")
    preds = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    
    print("\n--- Evaluation Metrics ---")
    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²:   {r2:.2f}")
    
    print("\n--- Feature Importance ---")
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    for i in range(min(10, len(feature_cols))):
        print(f"{i+1}. {feature_cols[indices[i]]}: {importances[indices[i]]:.4f}")
        
    # Save model and metadata
    os.makedirs(model_dir, exist_ok=True)
    artifacts = {
        'model': model,
        'features': feature_cols,
        'loc_avgs': loc_avgs
    }
    model_path = os.path.join(model_dir, 'traffic_model.joblib')
    joblib.dump(artifacts, model_path)
    print(f"\nModel artifacts saved to {model_path}")
    
    return model, feature_cols, mae, rmse, r2

if __name__ == "__main__":
    train_model()
