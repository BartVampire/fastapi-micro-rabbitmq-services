from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime, UTC
from fastapi import HTTPException, status
from typing import List, Optional
from core.models import Tier
from core.schemas.tier_schemas import TierCreate, TierUpdate


class CRUDTier:
    async def get_tiers(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Tier]:
        """Получение списка уровней с разбивкой на страницы"""
        result = await db.execute(select(Tier).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_tier(self, db: AsyncSession, tier_id: int) -> Tier:
        """Получение уровня по ID"""
        result = await db.execute(select(Tier).where(Tier.id == tier_id))
        return result.scalar_one_or_none()

    async def get_tier_by_name(self, db: AsyncSession, name: str) -> Optional[Tier]:
        """Получение уровня по имени"""
        result = await db.execute(select(Tier).where(Tier.name == name))
        return result.scalar_one_or_none()

    async def create_tier(self, db: AsyncSession, tier_in: TierCreate) -> Tier:
        """Создание нового уровня"""
        # Проверка уникальности имени уровня в БД
        existing_tier = await self.get_tier_by_name(db, tier_in.name)
        if existing_tier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Уровень с именем '{tier_in.name}' уже существует",
            )

        # Создаем новый уровень
        db_tier = Tier(name=tier_in.name, created_at=datetime.now())
        db.add(db_tier)
        await db.commit()
        await db.refresh(db_tier)
        return db_tier

    async def update_tier(
        self, db: AsyncSession, tier_id: int, tier_update: TierUpdate
    ) -> Tier:
        """Обновление уровня по ID"""
        # Получаем уровень из БД по ID и проверяем его наличие
        db_tier = await self.get_tier(db, tier_id)
        if not db_tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Уровень с id {tier_id} не найден",
            )

        # Если в запросе был передан новый название уровня, проверяем его уникальность в БД
        if tier_update.name and tier_update.name != db_tier.name:
            existing_tier = await self.get_tier_by_name(db, tier_update.name)
            if existing_tier:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Уровень с именем '{tier_update.name}' уже существует",
                )

        # Обновляем данные уровня
        update_data = tier_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now()

        query = (
            update(Tier).where(Tier.id == tier_id).values(**update_data).returning(Tier)
        )
        result = await db.execute(query)
        updated_tier = result.scalar_one()
        await db.commit()

        return updated_tier

    async def delete_tier(self, db: AsyncSession, tier_id: int) -> None:
        """Удаление уровня по ID"""
        # Проверяем существование уровня в БД
        db_tier = await self.get_tier(db, tier_id)
        if not db_tier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Уровень с id {tier_id} не найден",
            )

        # Удаляем уровень из БД
        await db.execute(delete(Tier).where(Tier.id == tier_id))
        await db.commit()


# Создаем экземпляр класса
tier_crud = CRUDTier()
