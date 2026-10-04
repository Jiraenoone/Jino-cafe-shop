"""
schemas/order.py — Pydantic schemas สำหรับ Order

รองรับ guest checkout และ selected_options JSON
"""
import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.order import OrderStatus


# ── OrderItem schemas ─────────────────────────────────────────────
class OrderItemCreate(BaseModel):
    """รายการสินค้าที่ลูกค้าส่งมา"""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=20)
    selected_options: dict[str, Any] | None = Field(
        None,
        examples=[{"size": "L", "temperature": "iced", "sweetness": "75%"}],
    )
    notes: str | None = Field(None, max_length=500)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: float
    selected_options: dict[str, Any] | None = None
    notes: str | None = None

    # product name สำหรับแสดงผล (join จาก relationship)
    product_name: str | None = None

    @field_validator("selected_options", mode="before")
    @classmethod
    def parse_options_json(cls, v: Any) -> Any:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v

    @field_validator("product_name", mode="before")
    @classmethod
    def extract_product_name(cls, v: Any, info: Any) -> Any:
        """ดึง product name จาก relationship ถ้ามี"""
        return v


# ── Order schemas ─────────────────────────────────────────────────
class OrderCreate(BaseModel):
    """Request body สำหรับ POST /api/orders"""
    customer_name: str = Field(..., min_length=1, max_length=200, examples=["Alice"])
    customer_email: EmailStr = Field(..., examples=["alice@example.com"])
    customer_phone: str | None = Field(None, max_length=20)
    notes: str | None = Field(None, max_length=500)
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderStatusUpdate(BaseModel):
    """Request body สำหรับ PATCH /api/admin/orders/{id}/status"""
    status: OrderStatus

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: OrderStatus) -> OrderStatus:
        return v


class OrderResponse(BaseModel):
    """Response object สำหรับออเดอร์"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    customer_email: str
    customer_phone: str | None = None
    status: str
    total_amount: float
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []


class OrderCreatedResponse(BaseModel):
    """Response หลังจากสร้างออเดอร์สำเร็จ"""
    id: int
    status: str
    total_amount: float
    created_at: datetime
    message: str = "Order placed successfully. You will receive a confirmation shortly."


class OrderListResponse(BaseModel):
    """Response สำหรับ list ของ orders"""
    items: list[OrderResponse]
    total: int
