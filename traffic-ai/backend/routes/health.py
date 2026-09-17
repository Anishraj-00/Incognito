from fastapi import APIRouter
from config.settings import settings

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
    System status, including ML service availability.
    """
    return {
        "api": "online",
        "version": settings.api_version,
        "ml_service": "available" # TODO: Developer 3 to implement actual ML check
    }
