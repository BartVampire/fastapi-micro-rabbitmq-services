import uuid
import logging
from typing import Annotated
from fastapi import Cookie, Depends
from sqlalchemy import select
from core.models import user_model, db_helper
from sqlalchemy.ext.asyncio import AsyncSession
from core.schemas import user_schemas
from auth_utils import utils_jwt
from user_publisher import UserPublisher, UserEvent
from core.schemas import AuthUserSchema
from user_rabbit import user_config

log = logging.getLogger(__name__)


class CRUDUser:
    def __init__(self):
        self.publisher = UserPublisher(config=user_config)

    async def get_user_me_by_token(
        self,
        db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
        access_token: str | bytes = Cookie(None),
    ):
        try:
            token_info = utils_jwt.decode_jwt(token=access_token)
            username = token_info.get("username")
            return await self.get_user_by_field(db=db, field="username", value=username)
        except Exception as e:
            log.error(f"Ошибка получения пользователя по токену: {e}")
            return None

    async def get_user(self, db: AsyncSession, user_uuid: uuid.UUID):
        result = await db.execute(
            select(user_model.User).where(user_model.User.uuid == user_uuid)
        )
        return result.scalars().first()

    async def get_user_by_field(self, db: AsyncSession, field: str, value: str):
        if field == "email":
            result = await db.execute(
                select(user_model.User).where(user_model.User.email == value)
            )
            return result.scalars().first()
        if field == "id":
            result = await db.execute(
                select(user_model.User).where(user_model.User.id == value)
            )
            return result.scalars().first()
        if field == "username":
            result = await db.execute(
                select(user_model.User).where(user_model.User.username == value)
            )
            return result.scalars().first()
        if field == "phone_number":
            result = await db.execute(
                select(user_model.User).where(user_model.User.phone_number == value)
            )
            return result.scalars().first()

    async def create_user(self, db: AsyncSession, user: user_schemas.UserCreate):
        secret_password = utils_jwt.hash_password(user.password)
        db_user = user_model.User(
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            hashed_password=secret_password,
            email=user.email,
            phone_number=user.phone_number,
            is_active=False,
            is_superuser=False,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        # Отправляем событие в auth сервис
        auth_user = AuthUserSchema(
            username=db_user.username,
            phone_number=db_user.phone_number,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_superuser=db_user.is_superuser,
            tier_id=1,  # Установите соответствующее значение
        )

        try:
            response = await self.publisher.publish_user_event(
                UserEvent.CREATED, auth_user
            )
        except Exception as e:
            log.error(f"Ошибка при отправке события в auth сервис: {str(e)}")

        return db_user

    async def update_user(
        self,
        db: AsyncSession,
        db_user: user_model.User,
        user_update: user_schemas.UserUpdate,
    ):
        # Обновляем данные пользователя
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        await db.commit()
        await db.refresh(db_user)

        # Отправляем событие в auth сервис
        auth_user = AuthUserSchema(
            username=db_user.username,
            phone_number=db_user.phone_number,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_superuser=db_user.is_superuser,
        )

        try:
            response = await self.publisher.publish_user_event(
                UserEvent.UPDATED, auth_user
            )
            if response and response.get("status") == "error":
                log.error(
                    f"Ошибка синхронизации с auth сервисом: {response.get('message')}"
                )
        except Exception as e:
            log.error(f"Ошибка при отправке события обновления в auth сервис: {str(e)}")

        return db_user

    async def delete_user(self, db: AsyncSession, user_uuid: uuid.UUID):
        db_user = await self.get_user(db=db, user_uuid=user_uuid)
        if not db_user:
            return None

        # Создаем auth_user до удаления из базы
        auth_user = AuthUserSchema(
            username=db_user.username,
            phone_number=db_user.phone_number,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            is_superuser=db_user.is_superuser,
            tier_id=1,  # Используйте актуальное значение из db_user если оно есть
        )

        # Удаляем пользователя из базы данных
        await db.delete(db_user)
        await db.commit()
        # Отправляем событие в auth сервис
        try:
            response = await self.publisher.publish_user_event(
                UserEvent.DELETED, auth_user
            )
            if response and response.get("status") == "error":
                log.error(
                    f"Ошибка синхронизации с auth сервисом: {response.get('message')}"
                )
        except Exception as e:
            log.error(f"Ошибка при отправке события удаления в auth сервис: {str(e)}")

        return {"message": "Пользователь успешно удален."}


crud_user = CRUDUser()
