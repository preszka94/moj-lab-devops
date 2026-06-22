"""
FastAPI backend for trader-workstation-platform.

This is the core API for the trading desk support system.
Traders and support staff use this API to fetch prices, manage risk, and execute trades.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List

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


class Position(BaseModel):
    """Represents a trading position."""
    symbol: str
    quantity: int
    avg_price: float
    current_price: float


@app.get("/", response_model=MessageResponse)
async def root():
    """
    Root endpoint.
    Returns a simple acknowledgment that the backend is running.
    """
    return {
        "message": "trader-workstation-platform backend ok",
        "timestamp": datetime().isoformat(),
    }


@app.get("/health", response_model=HealthStatus)
async def health():
    """
    Health check endpoint.
    Used by orchestration systems (Docker, Kubernetes) to verify the service is alive.
    """
    return {
        "status": "healthy",
        "timestamp": datetime().isoformat(),
        "service": "trader-workstation-platform",
    }

@app.get("/positions", response_model=List[Position])
async def get_positions():
    """
    Get current trading positions.
    In a real implementation, this would fetch data from a database or external service.
    Here we return hardcoded sample data for demonstration purposes.
    """
    return [
        Position(symbol="INGA.AS", quantity=1000, avg_price=14.20, current_price=14.85),
        Position(symbol="ASML.AS", quantity=15, avg_price=650.00, current_price=668.50),
        Position(symbol="DBR 0% 2032", quantity=500000, avg_price=96.80, current_price=97.35),
        Position(symbol="EURUSD", quantity=1000000, avg_price=1.0850, current_price=1.0892),
    ]

if __name__ == "__main__":
    import uvicorn

    # For local development only. In production, use docker-compose or orchestration.
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
