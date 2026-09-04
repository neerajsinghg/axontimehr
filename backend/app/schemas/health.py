from typing import Optional, Dict, Any
from pydantic import BaseModel

class ServiceHealthStatus(BaseModel):
    status: str
    latency_ms: Optional[float] = None
    details: Optional[str] = None

class HealthCheckResponse(BaseModel):
    success: bool = True
    message: str
    version: str = "1.0.0"
    environment: str
    services: Dict[str, ServiceHealthStatus]
    timestamp: str
    request_id: Optional[str] = None
