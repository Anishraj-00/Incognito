from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    api_title: str = "TrafficAI — Traffic Congestion Prediction API"
    api_version: str = "1.0.0"
    api_description: str = "API for predicting traffic congestion."
    debug_mode: bool = True
    cors_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
