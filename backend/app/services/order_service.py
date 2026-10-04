"""
services/order_service.py — Business logic สำหรับ Order

Service layer: ไม่รู้จัก HTTP, ไม่รู้จัก DB details
รับผิดชอบ business rules เท่านั้น
"""
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.messaging.publisher import publish_order_created
from app.models.order import Order, OrderStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import OrderCreate

logger = logging.getLogger(__name__)


class OrderService:
    """Business logic สำหรับ order management"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.order_repo = OrderRepository(db)
        self.product_repo = ProductRepository(db)

    async def create_order(self, data: OrderCreate) -> Order:
        """
        สร้างออเดอร์ใหม่:
        1. Validate ว่า products มีอยู่จริงและ available
        2. คำนวณ total_amount จากราคาใน DB (ไม่เชื่อจาก client)
        3. บันทึกลง database
        4. ส่ง message ไปยัง Service Bus (async — ไม่บล็อก response)
        """
        # ── Step 1: Validate products ────────────────────────────
        total_amount = 0.0
        for item in data.items:
            product = await self.product_repo.get_by_id(item.product_id)
            if not product:
                raise ValueError(f"Product ID {item.product_id} not found")
            if not product.is_available:
                raise ValueError(
                    f"Product '{product.name}' is currently not available"
                )
            total_amount += float(product.price) * item.quantity

        total_amount = round(total_amount, 2)

        # ── Step 2: Save order to database ───────────────────────
        order = await self.order_repo.create(data, total_amount)
        logger.info(
            "Order created | order_id=%d | customer=%s | total=%.2f",
            order.id,
            data.customer_email,
            total_amount,
        )

        # ── Step 3: Publish to Service Bus (fire-and-forget) ─────
        # การ publish ล้มเหลว ไม่ทำให้ order fail
        # customer ได้รับ response ทันที
        published = await publish_order_created(
            order_id=order.id,
            customer_name=data.customer_name,
            customer_email=data.customer_email,
            total_amount=total_amount,
            items_count=len(data.items),
        )
        if not published:
            logger.warning(
                "Order %d saved but Service Bus publish failed — worker will not process",
                order.id,
            )

        return order

    async def update_status(self, order_id: int, new_status: OrderStatus) -> Order:
        """
        อัปเดต status ของ order พร้อม validate transitions

        Valid transitions:
        PENDING → CONFIRMED, CANCELLED
        CONFIRMED → PREPARING, CANCELLED
        PREPARING → READY, CANCELLED
        READY → COMPLETED, CANCELLED
        COMPLETED → (ไม่สามารถเปลี่ยนได้)
        CANCELLED → (ไม่สามารถเปลี่ยนได้)
        """
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        current = OrderStatus(order.status)

        # Terminal states — ไม่สามารถเปลี่ยนได้แล้ว
        if current in (OrderStatus.COMPLETED, OrderStatus.CANCELLED):
            raise ValueError(
                f"Cannot change status from {current.value} — order is finalized"
            )

        # Validate transition
        valid_transitions: dict[OrderStatus, list[OrderStatus]] = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
            OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
            OrderStatus.READY: [OrderStatus.COMPLETED, OrderStatus.CANCELLED],
        }

        allowed = valid_transitions.get(current, [])
        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition: {current.value} → {new_status.value}. "
                f"Allowed: {[s.value for s in allowed]}"
            )

        updated_order = await self.order_repo.update_status(order, new_status)
        logger.info(
            "Order status updated | order_id=%d | %s → %s",
            order_id,
            current.value,
            new_status.value,
        )
        return updated_order
