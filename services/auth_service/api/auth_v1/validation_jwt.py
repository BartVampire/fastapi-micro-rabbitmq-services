import logging
from typing import Tuple

from fastapi import Depends, Request, Cookie, HTTPException, status
from jwt import InvalidTokenError

from api.auth_v1.auth_token_helpers import TOKEN_TYPE_FIELD
from auth_utils.refresh_token_check import (
    check_and_refresh_token_dependency,
)
from auth_utils import utils_jwt

logger = logging.getLogger(__name__)


async def get_current_token_payload(
    # token: str | bytes = Depends(oauth2_scheme),
    access_token: Tuple[Request, str | bytes] = Depends(
        check_and_refresh_token_dependency
    ),
    refresh_token: str | bytes = Cookie(None),
):
    try:
        _, access_token = access_token
        if not access_token and not refresh_token:
            # Выбрасываем исключение, чтобы на уровне маршрута выполнить редирект
            raise HTTPException(
                status_code=status.HTTP_302_FOUND, detail="Пожалуйста, авторизуйтесь."
            )

        payload = utils_jwt.decode_jwt(token=access_token)
        return payload

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный токен.",
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке токена: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при проверке токена",
        )


def validate_token_type(payload: dict, token_type: str | bytes) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Тип токена неверный."
    )
