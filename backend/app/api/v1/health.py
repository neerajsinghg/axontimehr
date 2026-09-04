from datetime import datetime, timezone
import time
from fastapi import APIRouter, Request, status
from app.core.config import settings
from app.db.session import check_database_connection
from app.services.redis import redis_service
from app.schemas.health import HealthCheckResponse, ServiceHealthStatus

router = APIRouter()

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Returns backend system health status, DB connectivity, and Redis connectivity."
)
async def health_check(request: Request) -> HealthCheckResponse:
    request_id = getattr(request.state, "request_id", None)
    
    # Check Database
    db_start = time.perf_counter()
    db_ok = await check_database_connection()
    db_latency = round((time.perf_counter() - db_start) * 1000, 2)
    
    # Check Redis
    redis_start = time.perf_counter()
    redis_ok = await redis_service.ping()
    redis_latency = round((time.perf_counter() - redis_start) * 1000, 2)
    
    overall_success = db_ok and redis_ok
    
    return HealthCheckResponse(
        success=overall_success,
        message="AxonTime HR API is healthy" if overall_success else "AxonTime HR API degraded service",
        version="1.0.0",
        environment=settings.APP_ENV,
        services={
            "database": ServiceHealthStatus(
                status="healthy" if db_ok else "unhealthy",
                latency_ms=db_latency if db_ok else None
            ),
            "redis": ServiceHealthStatus(
                status="healthy" if redis_ok else "unhealthy",
                latency_ms=redis_latency if redis_ok else None
            )
        },
        timestamp=datetime.now(timezone.utc).isoformat(),
        request_id=request_id
    )
