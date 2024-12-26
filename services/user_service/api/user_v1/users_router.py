import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.schemas import user_schemas
from .users_crud import crud_user
from core.models import db_helper, user_model

router = APIRouter(
    tags=["user"],
)


@router.get("/test")
def testing():
    return {"message": "test"}


@router.get("/me")
def auth_user_check_self_info(
    user: Annotated[user_schemas.UserRead, Depends(crud_user.get_user_me_by_token)],
):
    """Получение информации о пользователе"""
    # iat_ts = datetime.fromtimestamp(timestamp=payload.get("iat"))
    # iat = iat_ts.strftime("%H:%M:%S - %d.%m.%Y")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не авторизован.",
        )
    return {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "username": user.username,
        "email": user.email,
    }


@router.post(
    "/register",
    response_model=user_schemas.UserCreateInternal,
    response_model_exclude={"hashed_password"},
)
async def auth_user_register(
    user: user_schemas.UserCreate,
    db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    """Регистрация нового пользователя"""
    db_user_email = await crud_user.get_user_by_field(
        db=db, field="email", value=user.email
    )
    db_user_username = await crud_user.get_user_by_field(
        db=db, field="username", value=user.username
    )
    db_user_phone = await crud_user.get_user_by_field(
        db=db, field="phone_number", value=user.phone_number
    )

    if db_user_email or db_user_username or db_user_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже существует.",
        )
    return await crud_user.create_user(db=db, user=user)


@router.put("/{user_id}", response_model=user_schemas.UserUpdateInternal)
async def auth_user_update(
    user_id: uuid.UUID,
    user_update: user_schemas.UserUpdate,
    current_user: Annotated[user_model.User, Depends(crud_user.get_user_me_by_token)],
    db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    """Обновление информации о пользователе"""
    db_user = await crud_user.get_user(db=db, user_uuid=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден.",
        )

    if db_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав.")

    return await crud_user.update_user(db=db, db_user=db_user, user_update=user_update)


@router.delete(
    "/delete/{user_uuid}",
    response_model=UserDelete,
    dependencies=[Depends(get_superuser_auth)],
)
async def delete_user(
    user_uuid: uuid.UUID,
    db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    """Удаление пользователя"""
    user = await crud_user.get_user(db=db, user_uuid=user_uuid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден.",
        )
    return await crud_user.delete_user(db=db, user_uuid=user.uuid)
