"""
repositories/order_repository.py — Database operations สำหรับ Order
"""
import json
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, OrderStatus
from app.schemas.order import OrderCreate


class OrderRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(
        self,
        status: str | None = None,
        email: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Order], int]:
        """ดึง orders พร้อม filter"""
        query = select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )

        if status:
            query = query.where(Order.status == status)
        if email:
            query = query.where(Order.customer_email == email)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_by_id(self, order_id: int) -> Order | None:
        """ดึง order ตาม ID พร้อม items และ products"""
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: OrderCreate, total_amount: float) -> Order:
        """
        สร้าง order พร้อม items ทั้งหมดใน transaction เดียว
        total_amount คำนวณมาจาก service layer (ใช้ราคาจาก DB ไม่ใช่จาก client)
        """
        order = Order(
            customer_name=data.customer_name,
            customer_email=data.customer_email,
            customer_phone=data.customer_phone,
            notes=data.notes,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
        )
        self.db.add(order)
        await self.db.flush()  # ได้ order.id กลับมา

        # สร้าง order items
        for item_data in data.items:
            # ดึงราคาจาก DB (ไม่เชื่อราคาจาก client)
            from app.models.product import Product
            product_result = await self.db.execute(
                select(Product).where(Product.id == item_data.product_id)
            )
            product = product_result.scalar_one_or_none()
            if not product:
                raise ValueError(f"Product {item_data.product_id} not found")

            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=float(product.price),
                selected_options=(
                    json.dumps(item_data.selected_options)
                    if item_data.selected_options
                    else None
                ),
                notes=item_data.notes,
            )
            self.db.add(order_item)

        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def update_status(self, order: Order, new_status: OrderStatus) -> Order:
        """อัปเดต status ของ order"""
        order.status = new_status
        await self.db.flush()
        await self.db.refresh(order)
        return order
