# TrafficAI Backend API Documentation

Welcome to the TrafficAI Backend API. This API is built with FastAPI and provides predictions for traffic congestion.

## 1. Backend Startup

To run the API server locally:

```bash
uvicorn backend.main:app --reload
```

The server will start on `http://127.0.0.1:8000` by default.

## 2. API Documentation

FastAPI automatically generates interactive API documentation. Once the server is running, you can access:

*   **Swagger UI (Interactive):** `GET /docs`
*   **ReDoc (Static):** `GET /redoc`

## 3. Health Endpoint

Check if the API is running and reachable. This endpoint does NOT depend on the ML model.

**Endpoint:** `GET /health`

**Example Response:**
```json
{
  "status": "healthy",
  "service": "traffic-ai-api"
}
```

## 4. Status Endpoint

Check the overall system status, including the availability of the Machine Learning service.

**Endpoint:** `GET /api/v1/status`

**Example Response:**
```json
{
  "api": "online",
  "version": "1.0.0",
  "ml_service": "available"
}
```

## 5. Prediction Endpoint

The main endpoint to request traffic congestion predictions.

**Endpoint:** `POST /api/v1/predict`

**Request Schema:**
*(Note: As defined by the frontend contract; Developer 3 is responsible for the actual Pydantic schema implementation in `backend/schemas/prediction.py`)*

```json
{
  "location_id": "Jubilee Hills",
  "timestamp": "2026-09-17T12:00:00Z",
  "volume": 125,
  "speed": 24.5
}
```

**Expected Response Schema:**
```json
{
  "location": "Jubilee Hills",
  "timestamp": "2026-09-17T12:00:00Z",
  "predicted_traffic": 175,
  "congestion_level": "High",
  "congestion_index": 0.85,
  "confidence": 0.92,
  "uncertainty": 10.5,
  "explanation": [
    "Predicted traffic is significantly above average.",
    "Evening peak period."
  ],
  "status": "success"
}
```

## 6. Developer 3 Integration Contract

The `POST /api/v1/predict` route delegates the actual ML prediction to the service layer.

**Target File:** `backend/services/prediction_service.py`
**Target Function:** `predict_congestion(request: PredictionRequest) -> PredictionResponse`

**Integration Instructions:**
1. Developer 3 must implement the `PredictionRequest` and `PredictionResponse` Pydantic models in `backend/schemas/prediction.py`.
2. Developer 3 must implement the `predict_congestion` function in `backend/services/prediction_service.py`.
3. The function will receive a validated `PredictionRequest` object (containing the input features).
4. The function must invoke the real ML model (e.g., from `ml/predict.py`).
5. The function must return a structured `PredictionResponse` object.
6. **Error Handling:** If the ML model fails, the service can raise an exception, which will be caught by the route and returned as an HTTP 500 error. For validation errors, raise `HTTPException(status_code=400)`.

## 7. Frontend Integration (Developer 4)

Streamlit (Developer 4) should interact with the API as follows:

*   **Endpoint:** `http://127.0.0.1:8000/api/v1/predict`
*   **Method:** `POST`
*   **Headers:** `Content-Type: application/json`
*   **Body (JSON):** Must match the Request Schema described in Section 5.
*   **Response:** You will receive the JSON Response Schema described in Section 5. The API handles CORS natively, so requests from `http://localhost:8501` are permitted.

*Example call in Python (requests):*
```python
import requests

url = "http://127.0.0.1:8000/api/v1/predict"
payload = {
    "location_id": "Jubilee Hills",
    "volume": 125,
    "speed": 24.5
}
response = requests.post(url, json=payload)
data = response.json()
print(data["predicted_traffic"])
```
