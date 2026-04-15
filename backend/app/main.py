import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import router
from app.core.config import settings
from app.core.csrf import OriginCheckMiddleware
from app.core.exceptions import AppError
from app.core.logging import RequestLoggingMiddleware, setup_logging

setup_logging()
logger = logging.getLogger("finhub")

app = FastAPI(title=settings.app_name)

app.add_middleware(OriginCheckMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error_code": "internal_error", "detail": "An unexpected error occurred"},
    )


app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"app": settings.app_name, "status": "ok"}
