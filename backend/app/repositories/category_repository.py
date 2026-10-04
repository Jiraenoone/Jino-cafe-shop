"""
repositories/category_repository.py — Database operations สำหรับ Category
"""
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self, active_only: bool = True) -> Sequence[Category]:
        query = select(Category)
        if active_only:
            query = query.where(Category.is_active == True)  # noqa: E712
        query = query.order_by(Category.sort_order, Category.name)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, category_id: int) -> Category | None:
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: CategoryCreate) -> Category:
        category = Category(**data.model_dump())
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def update(self, category: Category, data: CategoryUpdate) -> Category:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        await self.db.flush()
        await self.db.refresh(category)
        return category
