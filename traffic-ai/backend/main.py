from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from backend.routes import health, prediction

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
)

# CORS configuration for Streamlit frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(health.router)
app.include_router(prediction.router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint verifying API is running.
    """
    return {
        "message": "TrafficAI API is running",
        "version": settings.api_version,
        "status": "healthy"
    }
