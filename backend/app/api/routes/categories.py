"""
api/routes/categories.py — Category endpoints
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin
from app.database.connection import get_db
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)) -> list[CategoryResponse]:
    """ดึงหมวดหมู่ทั้งหมด"""
    repo = CategoryRepository(db)
    categories = await repo.get_all(active_only=True)
    return [CategoryResponse.model_validate(c) for c in categories]


@router.post(
    "/admin/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    """สร้าง category ใหม่ (Admin only)"""
    repo = CategoryRepository(db)
    category = await repo.create(data)
    logger.info("Category created | id=%d | name=%s", category.id, category.name)
    return CategoryResponse.model_validate(category)


@router.put(
    "/admin/categories/{category_id}",
    response_model=CategoryResponse,
    dependencies=[Depends(require_admin)],
)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    """อัปเดต category (Admin only)"""
    repo = CategoryRepository(db)
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    category = await repo.update(category, data)
    return CategoryResponse.model_validate(category)
