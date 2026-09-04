from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.error_handler import register_error_handlers
from app.api.v1.router import api_v1_router
from app.services.redis import redis_service
from app.db.session import init_db

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(f"Starting {settings.APP_NAME} backend service...")
    await init_db()
    yield
    logger.info(f"Shutting down {settings.APP_NAME} backend service...")
    await redis_service.close()

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Modern Attendance & HRMS SaaS Platform API",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan
    )

    # Middleware
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Error Handlers
    register_error_handlers(app)

    # V1 Routers
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return app

app = create_application()
