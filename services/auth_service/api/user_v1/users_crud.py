import asyncio
import uuid
from typing import Annotated

from fastapi.params import Depends
from sqlalchemy import select

from core.models import db_helper
from core.models.auth_user_model import User
from sqlalchemy.ext.asyncio import AsyncSession
from core.schemas.auth_user_schemas import AuthUserSchema


class CRUDUser:
    async def get_user(self, db: AsyncSession, user_uuid: uuid.UUID):
        result = await db.execute(select(User).where(User.uuid == user_uuid))
        return result.scalars().first()

    async def get_user_by_field(self, db: AsyncSession, field: str, value: str):
        if field == "email":
            result = await db.execute(select(User).where(User.email == value))
            return result.scalars().first()

        if field == "username":
            result = await db.execute(select(User).where(User.username == value))
            return result.scalars().first()
        if field == "phone_number":
            result = await db.execute(select(User).where(User.phone_number == value))
            return result.scalars().first()

    async def create_user(self, db: AsyncSession, user: AuthUserSchema):
        # Проверка, является ли хешированный пароль в байтах
        secret_password = user.hashed_password
        if not bytes(user.hashed_password):
            secret_password = user.hashed_password.encode(
                "utf-8"
            )  # Преобразуем в байты, если это не так
        db_user = User(
            username=user.username,
            hashed_password=secret_password,
            email=user.email,
            phone_number=user.phone_number,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            tier_id=user.tier_id,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def update_user(
        self,
        db: AsyncSession,
        db_user: User,
        user_update: AuthUserSchema,
    ):
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def delete_user(self, db: AsyncSession, user_uuid: uuid.UUID):
        db_user = await self.get_user(db=db, user_uuid=user_uuid)
        if db_user:
            await db.delete(db_user)
            await db.commit()
            return {"message": "Пользователь успешно удален."}
        return db_user


crud_user = CRUDUser()


async def main():
    # Создайте сессию базы данных
    print("Подключение к базе данных...")
    async with db_helper.session_factory() as db:  # Предполагается, что у вас есть функция для получения сессии
        user = AuthUserSchema(
            username="admin",
            phone_number="+79288888888",
            email="admin@ya.ru",
            hashed_password=b"hello$2b$12$iiMydAFDphG1aLfleNk6Kun9YGUyYLjMI6F.ldrbSw7H5aezX/HDS",
            is_active=True,
            is_superuser=True,
            tier_id=1,
        )
        # Вызовите функцию создания пользователя
        print(f"Пользователь для создания: {user}")
        created_user = await crud_user.create_user(db=db, user=user)
        print(f"User created: {created_user}")


if __name__ == "__main__":
    asyncio.run(main())
