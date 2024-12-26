import datetime

from core.config import settings
from auth_utils import utils_jwt
from core.schemas import auth_user_schemas


TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access_token"
REFRESH_TOKEN_TYPE = "refresh_token"


# Функция для создания JWT токена
def create_jwt_token(
    token_type: str,
    payload: dict,
    expire_minutes: int = settings.auth.access_token_expires_minutes,
    expire_timedelta: datetime.timedelta | None = None,
) -> bytes:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(payload)
    return utils_jwt.encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


# Функция для создания JWT токена (access_token)
def create_access_token(user: auth_user_schemas.AuthUserSchema) -> bytes:
    jwt_payload = {
        "sub": user.username,
    }
    return create_jwt_token(
        token_type=ACCESS_TOKEN_TYPE,
        payload=jwt_payload,
        expire_minutes=settings.auth.access_token_expires_minutes,
    )


# Функция для создания JWT токена (refresh_token)
def create_refresh_token(user: auth_user_schemas.AuthUserSchema) -> bytes:
    jwt_payload = {
        "sub": user.username,
    }
    return create_jwt_token(
        token_type=REFRESH_TOKEN_TYPE,
        payload=jwt_payload,
        expire_timedelta=datetime.timedelta(
            days=settings.auth.refresh_token_expires_days
        ),
    )
