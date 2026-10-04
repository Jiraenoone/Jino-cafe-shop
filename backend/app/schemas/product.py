"""
schemas/product.py — Pydantic schemas สำหรับ Product

รองรับ JSON options field สำหรับ drink customization
"""
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Base ──────────────────────────────────────────────────────────
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, examples=["Signature Latte"])
    description: str | None = Field(None, max_length=1000)
    image_url: str | None = Field(None, max_length=500)
    price: float = Field(..., gt=0, examples=[85.0])
    options: dict[str, Any] | None = Field(
        None,
        examples=[{"sizes": ["S", "M", "L"], "temperatures": ["hot", "iced"]}],
    )
    is_available: bool = True


# ── Request schemas ───────────────────────────────────────────────
class ProductCreate(ProductBase):
    """ใช้สำหรับ POST /admin/products"""
    category_id: int = Field(..., gt=0)


class ProductUpdate(BaseModel):
    """ใช้สำหรับ PUT /admin/products/{id}"""
    category_id: int | None = Field(None, gt=0)
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    image_url: str | None = None
    price: float | None = Field(None, gt=0)
    options: dict[str, Any] | None = None
    is_available: bool | None = None


# ── Response schemas ──────────────────────────────────────────────
class ProductResponse(ProductBase):
    """Response object ที่ส่งกลับไปให้ frontend"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    created_at: datetime
    updated_at: datetime

    @field_validator("options", mode="before")
    @classmethod
    def parse_options_json(cls, v: Any) -> Any:
        """แปลง JSON string จาก DB เป็น dict"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v


class ProductListResponse(BaseModel):
    """Response สำหรับ list ของ products"""
    items: list[ProductResponse]
    total: int
