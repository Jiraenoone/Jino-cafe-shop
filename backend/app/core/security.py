"""
core/security.py — Authentication helpers

MVP: ใช้ API Key สำหรับ admin endpoints
รองรับการอัปเกรดเป็น Azure AD ในอนาคต
"""
import secrets

from fastapi import Header, HTTPException, status

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def require_admin(x_admin_key: str = Header(..., alias="X-Admin-Key")) -> None:
    """
    Dependency สำหรับ admin endpoints
    ตรวจสอบ X-Admin-Key header

    Usage:
        @router.get("/admin/...", dependencies=[Depends(require_admin)])
    """
    settings = get_settings()

    # ใช้ secrets.compare_digest เพื่อป้องกัน timing attack
    if not secrets.compare_digest(x_admin_key, settings.admin_api_key):
        logger.warning("Admin auth failed — invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
