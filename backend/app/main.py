"""
main.py — FastAPI Application Entry Point

Jino Café Backend API
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import categories, orders, products
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.database.connection import init_db

# ── Setup logging ก่อนอื่นใด ─────────────────────────────────────
setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


# ── Application lifecycle ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Startup/Shutdown hooks
    - Startup: สร้าง DB tables (SQLite dev) + log info
    - Shutdown: cleanup resources
    """
    # Startup
    logger.info("🚀 Jino Café API starting | env=%s", settings.app_env)
    await init_db()
    logger.info("✅ Database ready")

    yield

    # Shutdown
    logger.info("👋 Jino Café API shutting down")


# ── FastAPI app ───────────────────────────────────────────────────
app = FastAPI(
    title="Jino Café API",
    description="REST API สำหรับระบบสั่งเครื่องดื่ม Jino Café",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    # ซ่อน /docs ใน production
    openapi_url="/openapi.json" if not settings.is_production else None,
)


# ── Middleware ────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ── Global exception handler ──────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all exception handler — log และ return 500"""
    logger.error(
        "Unhandled exception | method=%s | path=%s | error=%s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "type": "internal_error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred. Please try again later.",
        },
    )


# ── Routes ────────────────────────────────────────────────────────
API_PREFIX = "/api"

app.include_router(categories.router, prefix=API_PREFIX, tags=["Categories"])
app.include_router(products.router, prefix=API_PREFIX, tags=["Products"])
app.include_router(orders.router, prefix=API_PREFIX, tags=["Orders"])


# ── Health check ──────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint สำหรับ Azure Container Apps
    ACA จะ ping ที่นี่เพื่อตรวจสอบว่า container ยัง healthy ไหม
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.app_env,
    }


@app.get("/", tags=["Root"])
async def root() -> dict:
    return {
        "message": "☕ Welcome to Jino Café API",
        "docs": "/docs",
        "health": "/health",
    }
