"""
api/routes/orders.py — Order endpoints

Public:  POST /api/orders, GET /api/orders/{id}
Admin:   GET /api/admin/orders, PATCH /api/admin/orders/{id}/status
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin
from app.database.connection import get_db
from app.models.order import OrderStatus
from app.repositories.order_repository import OrderRepository
from app.schemas.order import (
    OrderCreate,
    OrderCreatedResponse,
    OrderListResponse,
    OrderResponse,
    OrderStatusUpdate,
)
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Public endpoints ──────────────────────────────────────────────

@router.post(
    "/orders",
    response_model=OrderCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
) -> OrderCreatedResponse:
    """
    สั่งซื้อสินค้า (Guest checkout — ไม่ต้อง login)

    Flow:
    1. Validate products
    2. คำนวณราคาจาก DB
    3. บันทึกออเดอร์
    4. ส่ง message ไปยัง Service Bus
    5. Return response ทันที (ไม่รอ worker)
    """
    try:
        service = OrderService(db)
        order = await service.create_order(data)
        return OrderCreatedResponse(
            id=order.id,
            status=order.status,
            total_amount=float(order.total_amount),
            created_at=order.created_at,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    email: str = Query(..., description="Email ที่ใช้สั่งออเดอร์ (สำหรับ guest verification)"),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    ดึงข้อมูลออเดอร์ตาม ID + email verification
    Guest ต้องใส่ email ที่ใช้สั่ง เพื่อ verify ว่าเป็นของตัวเอง
    """
    repo = OrderRepository(db)
    order = await repo.get_by_id(order_id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Guest verification — ตรวจสอบ email
    if order.customer_email.lower() != email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email does not match this order",
        )

    return _order_to_response(order)


# ── Admin endpoints ───────────────────────────────────────────────

@router.get(
    "/admin/orders",
    response_model=OrderListResponse,
    dependencies=[Depends(require_admin)],
)
async def list_orders_admin(
    status_filter: str | None = Query(None, alias="status"),
    email: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> OrderListResponse:
    """ดึงรายการออเดอร์ทั้งหมด (Admin only)"""
    # Validate status filter
    if status_filter and status_filter not in OrderStatus.__members__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {status_filter}",
        )

    repo = OrderRepository(db)
    orders, total = await repo.get_all(
        status=status_filter,
        email=email,
        skip=skip,
        limit=limit,
    )
    return OrderListResponse(
        items=[_order_to_response(o) for o in orders],
        total=total,
    )


@router.patch(
    "/admin/orders/{order_id}/status",
    response_model=OrderResponse,
    dependencies=[Depends(require_admin)],
)
async def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """อัปเดต status ออเดอร์ (Admin only) พร้อม validate transitions"""
    try:
        service = OrderService(db)
        order = await service.update_status(order_id, data.status)
        return _order_to_response(order)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


# ── Helper ────────────────────────────────────────────────────────

def _order_to_response(order) -> OrderResponse:
    """แปลง Order ORM object เป็น OrderResponse schema"""
    from app.schemas.order import OrderItemResponse

    items = []
    for item in order.items:
        item_resp = OrderItemResponse.model_validate(item)
        if item.product:
            item_resp.product_name = item.product.name
        items.append(item_resp)

    resp = OrderResponse.model_validate(order)
    resp.items = items
    return resp
