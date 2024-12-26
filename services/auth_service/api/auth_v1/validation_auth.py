from fastapi import Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from api.user_v1.users_crud import crud_user
from auth_utils import utils_jwt
from core.models import db_helper


async def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
    db: AsyncSession = Depends(db_helper.session_getter),
):
    un_authed_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неправильный логин или пароль.",
    )
    # Ищем пользователя в базе данных
    db_user = await crud_user.get_user_by_field(db=db, field="username", value=username)
    if db_user is None:
        raise un_authed_exception
    # Проверяем пароль пользователя
    if not utils_jwt.validate_password(
        password=password,
        hashed_password=db_user.hashed_password,
    ):
        raise un_authed_exception
    # Проверяем подтвержденный ли пользователь
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Не подтвержденный пользователь.",
        )
    return db_user
