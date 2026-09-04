from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import logger

def register_error_handlers(app: FastAPI) -> None:
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.warning(
            "HTTP exception occurred",
            extra={"status_code": exc.status_code, "detail": exc.detail, "request_id": request_id}
        )
        
        error_code = f"HTTP_{exc.status_code}"
        error_message = exc.detail
        error_details = None

        if isinstance(exc.detail, dict):
            error_code = exc.detail.get("code", error_code)
            error_message = exc.detail.get("message", str(exc.detail))
            error_details = exc.detail.get("details", None)

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "detail": exc.detail,
                "error": {
                    "code": error_code,
                    "message": str(error_message),
                    "details": error_details
                },
                "request_id": request_id
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.warning(
            "Request validation error",
            extra={"errors": exc.errors(), "request_id": request_id}
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request parameters or payload",
                    "details": exc.errors()
                },
                "request_id": request_id
            }
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        logger.error(
            "Unhandled exception occurred",
            exc_info=exc,
            extra={"request_id": request_id}
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": None
                },
                "request_id": request_id
            }
        )
