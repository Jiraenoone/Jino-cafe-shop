"""
repositories/product_repository.py — Database operations สำหรับ Product

Repository pattern: แยก database logic ออกจาก business logic
"""
import json
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    """จัดการ database operations ทั้งหมดสำหรับ Product"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(
        self,
        category_id: int | None = None,
        search: str | None = None,
        available_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Product], int]:
        """ดึง products พร้อม filter และ pagination"""
        query = select(Product)

        if available_only:
            query = query.where(Product.is_available == True)  # noqa: E712
        if category_id:
            query = query.where(Product.category_id == category_id)
        if search:
            query = query.where(
                Product.name.ilike(f"%{search}%")
                | Product.description.ilike(f"%{search}%")
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Product.name)
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_by_id(self, product_id: int) -> Product | None:
        """ดึง product ตาม ID"""
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ProductCreate) -> Product:
        """สร้าง product ใหม่"""
        product = Product(
            category_id=data.category_id,
            name=data.name,
            description=data.description,
            image_url=data.image_url,
            price=data.price,
            options=json.dumps(data.options) if data.options else None,
            is_available=data.is_available,
        )
        self.db.add(product)
        await self.db.flush()  # flush เพื่อได้ ID กลับมา
        await self.db.refresh(product)
        return product

    async def update(self, product: Product, data: ProductUpdate) -> Product:
        """อัปเดต product"""
        update_data = data.model_dump(exclude_unset=True)

        # แปลง options dict เป็น JSON string
        if "options" in update_data and update_data["options"] is not None:
            update_data["options"] = json.dumps(update_data["options"])

        for field, value in update_data.items():
            setattr(product, field, value)

        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def delete(self, product: Product) -> None:
        """Soft delete — แค่ disable ไม่ได้ลบจริง"""
        product.is_available = False
        await self.db.flush()
