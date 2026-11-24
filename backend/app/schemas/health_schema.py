from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class LivenessResponse(BaseModel):
    status: str


class HealthResponse(BaseModel):
    status: str
    database: str


class EmailDeliveryStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attempts: int
    failures: int
    consecutive_failures: int
    last_failure_at: datetime | None = None
    last_failure_type: str | None = None


class EmailHealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    provider: Literal["brevo", "smtp", "console"]
    password_reset: EmailDeliveryStatsResponse
