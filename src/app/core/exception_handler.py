from functools import wraps
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.domain.exceptions import InvalidPasswordException
from core.logger import get_logger

logger = get_logger()

def log_exception_decorator(func):
    @wraps(func)
    async def wrapper(request: Request, exc: Exception, *args, **kwargs):
        logger.error(f"Exception occurred: {exc}", extra={
            "request": {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": request.client.host if request.client else None,
            }
        })
        return await func(request, exc)
    return wrapper

def register_exception_handlers(app: FastAPI) -> None:
    """
    Register custom exception handlers for the FastAPI application.
    """
    
    @app.exception_handler(InvalidPasswordException)
    @log_exception_decorator
    async def invalid_password_exception_handler(request: Request, exc: InvalidPasswordException):
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "status": "error",
                "message": str(exc),
                "action": exc.action if exc.action else "Please provide a valid password."
            },
        )
