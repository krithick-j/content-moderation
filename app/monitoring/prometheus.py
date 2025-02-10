from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.responses import Response
from loguru import logger
from app.configs.log_config import setup_logger
from app.configs.db_config import get_async_db
from app.configs.redis_config import redis_client
from app.configs.celery_config import celery
from app.schemas.health import HealthCheckResponse

setup_logger()
metrics_router = APIRouter()

# Define Prometheus Metrics
REQUEST_COUNT = Counter(
    "request_count", "Total number of requests", ["method", "endpoint"]
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Request latency in seconds", ["endpoint"]
)

@metrics_router.get("/metrics")
def metrics():
    """Expose Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@metrics_router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_async_db)):
    """Health check endpoint for database, Redis, and Celery."""
    status = {"status": "healthy"}

    # Check Database Connection
    try:
        await db.execute(text('SELECT 1'))  # Executes a simple query to test DB connection
        status["database"] = "available"
    except Exception as e:
        status["status"] = "unhealthy"
        status["database"] = f"unavailable - {str(e)}"
        logger.error(f"Database connection error: {e}")

    # Check Redis Connection
    try:
        redis_client.ping()
        status["redis"] = "available"
    except Exception as e:
        status["status"] = "unhealthy"
        status["redis"] = f"unavailable - {str(e)}"
        logger.error(f"Redis connection error: {e}")

    # Check Celery Connection
    try:
        celery.control.ping(timeout=1)
        status["celery"] = "available"
    except Exception as e:
        status["status"] = "unhealthy"
        status["celery"] = f"unavailable - {str(e)}"
        logger.error(f"Celery connection error: {e}")

    return HealthCheckResponse(
        status=status["status"],
        database=status["database"],
        redis=status["redis"],
        celery=status["celery"]
    )