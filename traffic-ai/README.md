# TrafficAI — Traffic Congestion Prediction Agent

Welcome to the TrafficAI project! This project was designed for a 5-hour hackathon, aiming for a clean and efficient separation of concerns across Machine Learning, Backend API, and Frontend Visualization.

## Folder Structure

The project is structured to keep concerns separated and make it easy for multiple developers to work concurrently.

```text
traffic-ai/
├── backend/          # FastAPI application (API layer and business logic)
├── ml/               # Machine learning models, training, and inference scripts
├── data/             # Raw and processed datasets
├── models/           # Saved trained models (.pkl, .joblib, etc.)
├── frontend/         # Streamlit dashboard and UI components
├── config/           # Application-wide configuration and settings
├── tests/            # Unit tests for API and ML
├── notebooks/        # Jupyter notebooks for exploratory data analysis
├── scripts/          # Helper scripts (e.g., data fetching, setup)
└── ...
```

### Key Files and their Purpose

- `backend/main.py`: FastAPI application entry point.
- `backend/routes/`: API endpoints only (routing layer).
- `backend/services/`: Application and business logic.
- `backend/schemas/`: Pydantic models for request and response validation.
- `ml/train.py`: Model training pipeline.
- `ml/predict.py`: Inference logic for predicting traffic.
- `frontend/dashboard.py`: Streamlit entry point.
- `data/README.md`: Data documentation.
- `run.py`: General runner script for the app.
- `requirements.txt`: Initial python dependencies.
- `.env.example`: Template for environment variables.

## Suggested Team Ownership (4 Developers)

To maximize velocity over the 5-hour hackathon, here is a suggested distribution of ownership:

1. **Developer 1 (ML/Data Engineer):** 
   - **Ownership:** `ml/`, `data/`, `notebooks/`, `models/`
   - **Focus:** Data preprocessing, feature engineering, training the congestion classification model, and confidence estimation.

2. **Developer 2 (API/Backend Engineer):**
   - **Ownership:** `backend/routes/`, `backend/main.py`, `config/`
   - **Focus:** Setting up the FastAPI server, defining endpoints, and configuring application settings.

3. **Developer 3 (Backend Logic & Integration):**
   - **Ownership:** `backend/services/`, `backend/schemas/`, `tests/`
   - **Focus:** Connecting ML inference functions to the API, writing Pydantic models, handling business logic, and writing basic API tests.

4. **Developer 4 (Frontend/UI Engineer):**
   - **Ownership:** `frontend/`
   - **Focus:** Building the Streamlit dashboard, creating mapping and charting components, and integrating with the backend API via `utils/api_client.py`.
