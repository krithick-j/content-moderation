from pydantic import BaseModel
from typing import Literal

class HealthCheckResponse(BaseModel):
    status: Literal["healthy", "unhealthy"]
    database: str
    redis: str
    celery: str
