import logging

from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.auth_v1.auth_token_helpers import TOKEN_TYPE_FIELD
from core.models import db_helper, auth_user_model as user_model

logger = logging.getLogger(__name__)


def validate_token_type(payload: dict, token_type: str | bytes) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Тип токена неверный."
    )


async def get_user_by_token_sub(
    payload: dict, db: AsyncSession = Depends(db_helper.session_getter)
) -> user_model.User:
    try:
        username: str | None = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Вы не зарегистрированы.",
            )
        # Запрос к базе данных для поиска пользователя по имени
        result = await db.execute(
            select(user_model.User).where(user_model.User.username == username)
        )
        user = result.scalars().first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден.",
            )
        return user

    except Exception as e:
        logger.error(f"Ошибка при получении пользовательских данных: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении данных пользователя",
        )
