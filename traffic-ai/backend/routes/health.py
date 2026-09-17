from fastapi import APIRouter
from config.settings import settings
from backend.services.data_manager import DATA_FILE, MODEL_FILE

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check():
    """
    Check if the API is running.
    Does not depend on the ML model.
    """
    return {
        "status": "healthy",
        "service": "traffic-ai-api"
    }


@router.get("/api/v1/status", tags=["Health"])
def system_status():
    """
    System status including ML model and data availability.

    Performs a real filesystem check on whether the trained model artifact
    and synthetic traffic dataset exist on disk.
    """
    model_ready = MODEL_FILE.exists()
    data_ready = DATA_FILE.exists()

    return {
        "api": "online",
        "version": settings.api_version,
        "ml_service": "available" if model_ready else "unavailable",
        "model_file": str(MODEL_FILE) if model_ready else None,
        "data_ready": data_ready,
        "data_file": str(DATA_FILE) if data_ready else None,
    }
