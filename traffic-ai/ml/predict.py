import pandas as pd
import numpy as np
import joblib
from datetime import timedelta
import os
from ml.preprocess import preprocess_data
from ml.features import engineer_features
from ml.congestion import classify_congestion
from ml.confidence import estimate_confidence
import warnings

# Suppress warnings for simple prediction
warnings.filterwarnings('ignore')

def load_model_artifacts(model_dir="models"):
    model_path = os.path.join(model_dir, 'traffic_model.joblib')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")
    return joblib.load(model_path)

def generate_prediction_explanation(row, predicted_vol, feature_cols):
    """Generates simple text explanations for the prediction."""
    explanations = []
    
    if 'loc_hist_avg' in row.index:
        avg = row['loc_hist_avg']
        if predicted_vol > avg * 1.2:
            explanations.append(f"Predicted traffic is significantly above the historical average ({avg:.0f}) for this road segment.")
        elif predicted_vol < avg * 0.8:
            explanations.append(f"Predicted traffic is well below the historical average ({avg:.0f}).")
            
    if row.get('is_evening_peak', 0) == 1:
        explanations.append("The prediction falls within the evening peak period.")
    elif row.get('is_morning_peak', 0) == 1:
        explanations.append("The prediction falls within the morning peak period.")
        
    if row.get('is_weekend', 0) == 1:
        explanations.append("Weekend traffic patterns are in effect.")
        
    if row.get('traffic_change', 0) > 10:
        explanations.append("Traffic has been increasing recently.")
    elif row.get('traffic_change', 0) < -10:
        explanations.append("Traffic has been decreasing recently.")
        
    if not explanations:
        explanations.append("Traffic is expected to follow standard patterns.")
        
    return explanations

def forecast_traffic(location: str, current_data: pd.DataFrame, horizon=3, model_dir="models"):
    """
    Predicts traffic for the next `horizon` hours.
    current_data should contain recent history for this location to compute features.
    """
    artifacts = load_model_artifacts(model_dir)
    model = artifacts['model']
    feature_cols = artifacts['features']
    loc_avgs = artifacts['loc_avgs']
    
    # We need to iteratively predict
    df = current_data.copy()
    
    # Ensure it's for the right location
    df = df[df['location_id'] == location].sort_values('timestamp')
    if df.empty:
        raise ValueError(f"No data for location {location}")
        
    forecasts = []
    
    for i in range(horizon):
        # Engineer features on current state
        # We process the whole df each time to get correct lags/rolling
        df_feat = engineer_features(df.copy())
        
        # Add location average if missing
        if 'loc_hist_avg' not in df_feat.columns:
            df_feat['loc_hist_avg'] = loc_avgs.get(location, df_feat['volume'].mean())
            
        # One hot encode location
        loc_col = f'location_id_{location}'
        for c in feature_cols:
            if c.startswith('location_id_'):
                df_feat[c] = 1 if c == loc_col else 0
                
        # Fill missing weather
        for c in ['rainfall', 'temperature']:
            if c in feature_cols and c not in df_feat.columns:
                df_feat[c] = 0 # default fallback
                
        # Get the latest row for prediction
        latest_row = df_feat.iloc[-1].copy()
        
        # Predict t+1
        # Need to ensure all features are present
        X = pd.DataFrame([latest_row])[feature_cols]
        # Fill NaNs if any
        X = X.fillna(0)
        
        pred_vol = model.predict(X)[0]
        pred_vol = max(0, int(pred_vol))
        
        conf, std = estimate_confidence(model, X.iloc[0], pred_vol)
        explanations = generate_prediction_explanation(latest_row, pred_vol, feature_cols)
        
        next_timestamp = latest_row['timestamp'] + timedelta(hours=1)
        
        # Create a dummy row to evaluate congestion
        # We need to simulate congestion logic
        dummy_df = pd.DataFrame([{
            'location_id': location,
            'volume': pred_vol,
            'loc_hist_avg': latest_row['loc_hist_avg'],
            # Assume speed holds constant or drops
            'speed': latest_row.get('speed', 40)
        }])
        
        dummy_df = classify_congestion(dummy_df)
        congestion_level = dummy_df['congestion_level'].iloc[0]
        congestion_index = dummy_df['congestion_index'].iloc[0]
        
        forecasts.append({
            "location": location,
            "timestamp": str(next_timestamp),
            "predicted_traffic": pred_vol,
            "congestion_level": congestion_level,
            "congestion_index": float(congestion_index),
            "confidence": conf,
            "uncertainty": std,
            "explanation": explanations
        })
        
        # Append prediction to df for next iteration (recursive forecasting)
        new_row = df.iloc[-1].copy()
        new_row['timestamp'] = next_timestamp
        new_row['volume'] = pred_vol
        # In a real app we might forecast weather too, but here we just carry it forward
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
    return forecasts

def predict_traffic(location: str, current_data: pd.DataFrame, model_dir="models"):
    """Alias for a single-step forecast."""
    return forecast_traffic(location, current_data, horizon=1, model_dir=model_dir)[0]
