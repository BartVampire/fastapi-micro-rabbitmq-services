from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

#
# from app.api.auth_v1.validation_auth_helper import (
#     get_superuser_auth,
# )
from .tier_crud import tier_crud
from core.models import db_helper
from core.schemas import tier_schemas

router = APIRouter(
    tags=["Tiers"],
)


@router.get(
    "",
    response_model=list[tier_schemas.TierRead],
    # dependencies=[Depends(get_superuser_auth)],
)
async def get_all_tiers(
    db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    skip: int = 0,
    limit: int = 100,
):
    """Получение списка уровней с разбивкой на страницы"""
    return await tier_crud.get_tiers(db=db, skip=skip, limit=limit)


@router.get(
    "/{tier_id}",
    response_model=tier_schemas.TierRead,
    # dependencies=[Depends(get_superuser_auth)],
)
async def get_one_tier(
    tier_id: int, db: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    """Получение уровня по ID"""
    return await tier_crud.get_tier(db=db, tier_id=tier_id)


@router.post(
    "",
    response_model=tier_schemas.TierCreate,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(get_superuser_auth)],
)
async def create_tier(
    tier_in: tier_schemas.TierCreate,
    db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    """Создание нового уровня"""
    return await tier_crud.create_tier(db=db, tier_in=tier_in)


@router.patch(
    "/{tier_id}",
    response_model=tier_schemas.TierRead,
    # dependencies=[Depends(get_superuser_auth)],
)
async def update_tier(
    tier_id: int,
    tier_update: tier_schemas.TierUpdate,
    db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    """Обновление уровня по ID"""
    return await tier_crud.update_tier(db=db, tier_id=tier_id, tier_update=tier_update)


@router.delete(
    "/{tier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    # dependencies=[Depends(get_superuser_auth)],
)
async def delete_tier(
    tier_id: int,
    db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    """Удаление уровня по ID"""
    return await tier_crud.delete_tier(db=db, tier_id=tier_id)
