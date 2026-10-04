"""models/category.py — ORM Model สำหรับ Categories table"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Category(Base):
    __tablename__ = "Categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )

    # Relationship — Category มีหลาย Products
    products: Mapped[list["Product"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Product", back_populates="category", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"
