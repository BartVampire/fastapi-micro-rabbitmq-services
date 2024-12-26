import logging

from fastapi import Depends, HTTPException
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from api.auth_v1.auth_token_helpers import REFRESH_TOKEN_TYPE
from api.auth_v1.token_crud import is_token_blacklisted
from api.auth_v1.auth_utils import get_user_by_token_sub
from api.auth_v1.auth_utils import validate_token_type
from auth_utils import utils_jwt
from core.models import db_helper
from core.models.auth_user_model import User

logger = logging.getLogger(__name__)


async def get_current_token_payload_for_refresh(
    request: Request, db: AsyncSession = Depends(db_helper.session_getter)
) -> User:
    try:
        token = request.cookies.get("refresh_token")
        if not token or await is_token_blacklisted(db=db, refresh_token=token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неправильный токен.",
            )
        print(f"get_current_token_payload_for_refresh: {token}")
        payload = utils_jwt.decode_jwt(token=token)
    except InvalidTokenError as e:
        logger.error(f'Ошибка при проверке токена обновления: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный токен.",
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке токена обновления: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Внутренняя ошибка сервера при проверке токена",
        )

    return payload


async def get_current_auth_user_for_refresh(
    payload: dict = Depends(get_current_token_payload_for_refresh),
    db: AsyncSession = Depends(db_helper.session_getter),
) -> User:
    validate_token_type(payload=payload, token_type=REFRESH_TOKEN_TYPE)
    return await get_user_by_token_sub(payload=payload, db=db)
