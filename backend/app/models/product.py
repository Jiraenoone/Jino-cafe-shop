"""models/product.py — ORM Model สำหรับ Products table"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


class Product(Base):
    __tablename__ = "Products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("Categories.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    options: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # JSON string เก็บ options
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    category: Mapped["Category"] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "Category", back_populates="products"
    )
    order_items: Mapped[list["OrderItem"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        "OrderItem", back_populates="product"
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name!r} price={self.price}>"
