"""
schemas/category.py — Pydantic schemas สำหรับ Category

Request/Response DTOs สำหรับ Category endpoints
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ── Base ──────────────────────────────────────────────────────────
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Coffee"])
    description: str | None = Field(None, max_length=500)
    image_url: str | None = Field(None, max_length=500)
    sort_order: int = Field(default=0, ge=0)
    is_active: bool = True


# ── Request schemas ───────────────────────────────────────────────
class CategoryCreate(CategoryBase):
    """ใช้สำหรับ POST /admin/categories"""
    pass


class CategoryUpdate(BaseModel):
    """ใช้สำหรับ PUT /admin/categories/{id} — ทุก field optional"""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    image_url: str | None = None
    sort_order: int | None = Field(None, ge=0)
    is_active: bool | None = None


# ── Response schemas ──────────────────────────────────────────────
class CategoryResponse(CategoryBase):
    """Response object ที่ส่งกลับไปให้ frontend"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
