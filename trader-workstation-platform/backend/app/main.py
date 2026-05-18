"""
FastAPI backend for trader-workstation-platform.

This is the core API for the trading desk support system.
Traders and support staff use this API to fetch prices, manage risk, and execute trades.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(
    title="Trader Workstation Platform",
    description="Internal trading and risk support API for ING",
    version="0.1.0",
)


class HealthStatus(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    service: str


class MessageResponse(BaseModel):
    """Generic message response model."""
    message: str
    timestamp: str


@app.get("/", response_model=MessageResponse)
async def root():
    """
    Root endpoint.
    Returns a simple acknowledgment that the backend is running.
    """
    return {
        "message": "trader-workstation-platform backend ok",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health", response_model=HealthStatus)
async def health():
    """
    Health check endpoint.
    Used by orchestration systems (Docker, Kubernetes) to verify the service is alive.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "trader-workstation-platform",
    }


if __name__ == "__main__":
    import uvicorn

    # For local development only. In production, use docker-compose or orchestration.
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
