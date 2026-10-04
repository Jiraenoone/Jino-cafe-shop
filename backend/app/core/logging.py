"""
core/logging.py — ตั้งค่า structured logging

ใช้ Python logging standard library พร้อม JSON formatter
เพื่อให้ Azure Application Insights รับ log ได้ถูกต้อง
"""
import logging
import sys
from typing import Any

from app.core.config import get_settings


def setup_logging() -> None:
    """ตั้งค่า logging ระดับ application"""
    settings = get_settings()

    log_level = logging.DEBUG if settings.debug else logging.INFO

    # Format: [timestamp] [level] [logger] message {extra fields}
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # ลด noise จาก library ที่ verbose เกินไป
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.debug else logging.WARNING
    )
    logging.getLogger("azure").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(
        "Logging initialized | env=%s | debug=%s",
        settings.app_env,
        settings.debug,
    )


def get_logger(name: str) -> logging.Logger:
    """Helper สำหรับดึง logger ในแต่ละ module"""
    return logging.getLogger(name)
