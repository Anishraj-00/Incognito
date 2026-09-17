import os
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

# Determine the traffic-ai root directory reliably
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATA_FILE = DATA_DIR / "synthetic_traffic.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_FILE = MODEL_DIR / "traffic_model.joblib"

# Default segment geographical coordinates & descriptive names
SEGMENT_METADATA: Dict[str, Dict[str, Any]] = {
    "LOC_A": {
        "name": "Downtown Core Corridor (Main St)",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "free_flow_speed": 60.0
    },
    "LOC_B": {
        "name": "North Expressway (I-80 Interchange)",
        "latitude": 37.7858,
        "longitude": -122.4065,
        "free_flow_speed": 75.0
    },
    "LOC_C": {
        "name": "Harbor Bridge Approach",
        "latitude": 37.7925,
        "longitude": -122.3932,
        "free_flow_speed": 50.0
    }
}

_cached_df: Optional[pd.DataFrame] = None
_cached_artifacts: Optional[Dict[str, Any]] = None


def ensure_data_and_model_ready():
    """
    Guarantees synthetic data and trained model artifacts exist on disk.
    If not, automatically generates synthetic dataset and trains baseline model.
    """
    global _cached_df, _cached_artifacts

    if not DATA_FILE.exists():
        print(f"Data file not found at {DATA_FILE}. Generating synthetic traffic dataset...")
        os.makedirs(DATA_DIR, exist_ok=True)
        from ml.generate_data import generate_synthetic_traffic_data
        generate_synthetic_traffic_data(output_path=str(DATA_FILE), num_days=60)
        _cached_df = None

    if not MODEL_FILE.exists():
        print(f"Model file not found at {MODEL_FILE}. Training baseline traffic model...")
        os.makedirs(MODEL_DIR, exist_ok=True)
        from ml.train import train_model
        train_model(data_path=str(DATA_FILE), model_dir=str(MODEL_DIR))
        _cached_artifacts = None


def get_traffic_data(force_reload: bool = False) -> pd.DataFrame:
    """
    Returns preprocessed traffic DataFrame, cached in-memory.
    """
    global _cached_df
    if _cached_df is None or force_reload:
        ensure_data_and_model_ready()
        from ml.preprocess import preprocess_data
        _cached_df = preprocess_data(str(DATA_FILE))
    return _cached_df.copy()


def get_model_artifacts(force_reload: bool = False) -> Dict[str, Any]:
    """
    Returns loaded model artifacts, cached in-memory.
    """
    global _cached_artifacts
    if _cached_artifacts is None or force_reload:
        ensure_data_and_model_ready()
        from ml.predict import load_model_artifacts
        _cached_artifacts = load_model_artifacts(str(MODEL_DIR))
    return _cached_artifacts
