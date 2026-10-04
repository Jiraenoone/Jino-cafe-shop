"""
api/routes/products.py — Product endpoints

Public:  GET /api/products, GET /api/products/{id}
Admin:   POST, PUT, DELETE /api/admin/products
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin
from app.database.connection import get_db
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Public endpoints ──────────────────────────────────────────────

@router.get("/products", response_model=ProductListResponse)
async def list_products(
    category_id: int | None = Query(None, description="กรองตาม category"),
    search: str | None = Query(None, description="ค้นหาด้วยชื่อหรือ description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    """ดึงรายการสินค้าทั้งหมดที่ available"""
    repo = ProductRepository(db)
    products, total = await repo.get_all(
        category_id=category_id,
        search=search,
        available_only=True,
        skip=skip,
        limit=limit,
    )
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """ดึง product ตาม ID"""
    repo = ProductRepository(db)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found",
        )
    return ProductResponse.model_validate(product)


# ── Admin endpoints ───────────────────────────────────────────────

@router.post(
    "/admin/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """สร้าง product ใหม่ (Admin only)"""
    # ตรวจสอบว่า category มีอยู่จริง
    cat_repo = CategoryRepository(db)
    category = await cat_repo.get_by_id(data.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category {data.category_id} not found",
        )

    repo = ProductRepository(db)
    product = await repo.create(data)
    logger.info("Product created | id=%d | name=%s", product.id, product.name)
    return ProductResponse.model_validate(product)


@router.put(
    "/admin/products/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(require_admin)],
)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """อัปเดต product (Admin only)"""
    repo = ProductRepository(db)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    product = await repo.update(product, data)
    logger.info("Product updated | id=%d", product_id)
    return ProductResponse.model_validate(product)


@router.delete(
    "/admin/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft delete product (Admin only)"""
    repo = ProductRepository(db)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    await repo.delete(product)
    logger.info("Product disabled | id=%d", product_id)
