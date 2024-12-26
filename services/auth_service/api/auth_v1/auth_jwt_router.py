import logging
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from api.auth_v1.auth_token_helpers import (
    create_access_token,
    create_refresh_token,
)

from api.auth_v1.validation_auth import (
    validate_auth_user,
)
from api.auth_v1.validation_auth_helper import get_current_token_payload
from api.auth_v1.validation_auth_helper_refresh import (
    get_current_auth_user_for_refresh,
)
from api.auth_v1 import token_crud
from api.auth_v1.token_crud import add_tokens_to_db, is_token_blacklisted
from auth_utils import decode_jwt
from core.models import db_helper
from core.schemas import auth_user_schemas
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    Response,
    Cookie,
    Form,
)
from fastapi.security import (
    HTTPBearer,
)

from core.schemas.base_schemas import TokenInfo

http_bearer = HTTPBearer(auto_error=False)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jwt", tags=["auth"], dependencies=[Depends(http_bearer)])


@router.post("/login", response_model=TokenInfo)
async def auth_user_issue_jwt(
    response: Response,
    request: Request,
    db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: auth_user_schemas.AuthUserSchema = Depends(validate_auth_user),
    refresh_token: str | bytes = Cookie(None),
):
    if refresh_token and await is_token_blacklisted(db=db, refresh_token=refresh_token):
        response.delete_cookie("refresh_token")
        response.delete_cookie("access_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пожалуйста, перезапустите приложение.",
        )

    access_token = create_access_token(user=user)
    refresh_token = create_refresh_token(user=user)

    access_expires_at = datetime.fromtimestamp((decode_jwt(access_token)).get("exp"))
    refresh_expires_at = datetime.fromtimestamp((decode_jwt(refresh_token)).get("exp"))

    response.set_cookie(
        key="access_token",
        value=access_token.decode("utf-8"),
        httponly=True,  # Запрещает доступ к cookie через JavaScript
        secure=True,  # Для HTTPS
        samesite="strict",  # Значения: "lax", "strict", "none"
        # samesite - "lax": cookie отправляются при переходе на сайт извне
        # samesite - "strict": cookie отправляются только при переходах внутри сайта
        # samesite - "none": cookie отправляются всегда (требует secure=True)
        max_age=7200,  # Время жизни cookie в секундах (2 часа),
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token.decode("utf-8"),
        httponly=True,
        secure=True,  # Для HTTPS
        samesite="strict",
        max_age=30 * 24 * 3600,  # Время жизни cookie в секундах (30 дней),
    )

    await add_tokens_to_db(
        db=db,
        user=user,
        access_token=access_token,
        access_expires_at=access_expires_at,
        refresh_token=refresh_token,
        refresh_expires_at=refresh_expires_at,
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.client.host,
    )
    # Перенаправление на главную страницу
    response.headers["Location"] = "/docs"  # или любой другой путь
    response.status_code = (
        status.HTTP_303_SEE_OTHER
    )  # See Other - стандартный статус для перенаправления

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_at=access_expires_at,
        refresh_expires_at=refresh_expires_at,
    )


@router.post("/validate_token/")
async def validate_token_jwt(
    request: Request,
    response: Response,
    payload=Depends(get_current_token_payload),
):
    try:
        return payload
    except Exception as e:

        logger.error(f"Неожиданная ошибка при проверке токена: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пожалуйста, авторизуйтесь.",
        )


@router.post("/refresh", response_model=TokenInfo, response_model_exclude_none=True)
async def auth_refresh_jwt(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: auth_user_schemas.AuthUserSchema = Depends(get_current_auth_user_for_refresh),
    refresh_token: str | bytes = Cookie(None),
):
    try:
        if refresh_token:
            check_token = await is_token_blacklisted(db=db, refresh_token=refresh_token)
            if check_token is True:
                response.delete_cookie("refresh_token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Пожалуйста, авторизуйтесь.",
                )

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не передан токен для обновления.",
            )

        access_token = create_access_token(user=user)
        access_expires_at = datetime.fromtimestamp(
            (decode_jwt(access_token)).get("exp")
        )
        refresh_expires_at = datetime.fromtimestamp(
            (decode_jwt(refresh_token)).get("exp")
        )
        await add_tokens_to_db(
            db=db,
            user=user,
            access_token=access_token,
            access_expires_at=access_expires_at,
            refresh_token=refresh_token.encode("utf-8"),
            refresh_expires_at=refresh_expires_at,
            user_agent=request.headers.get("User-Agent"),
            ip_address=request.client.host,
        )

        response.set_cookie(
            key="access_token",
            value=access_token.decode("utf-8"),
            httponly=True,
            secure=True,  # Для HTTPS
            samesite="strict",
            max_age=1800,  # Время жизни cookie в секундах (30 минут),
        )

        return TokenInfo(
            access_token=access_token,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
        )

    except Exception as e:
        logger.info(
            f"Ошибка при обновлении токена: {str(e)}\nПользователь: {user.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Неправильный токен для обновления.",
        )


@router.post("/logout")
async def logout(
    response: Response,
    db: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    refresh_token: str | bytes = Cookie(None),
    access_token: str | bytes = Cookie(None),
):
    try:
        # Проверка наличия токенов
        if not refresh_token and not access_token:
            return {"message": "Вы уже вышли из системы"}

        if access_token:
            access_token = access_token.encode("utf-8")
        access_expires_at = datetime.fromtimestamp(
            (decode_jwt(access_token)).get("exp")
        )
        username = (decode_jwt(access_token)).get("sub")
        if refresh_token:
            refresh_token = refresh_token.encode("utf-8")
        refresh_expires_at = datetime.fromtimestamp(
            (decode_jwt(refresh_token)).get("exp")
        )
        check_token = await is_token_blacklisted(
            db=db, refresh_token=refresh_token, access_token=access_token
        )
        if check_token is False:
            # Добавляем оба токена в черный список
            await token_crud.add_tokens_to_blacklist(
                db=db,
                access_token=access_token,
                refresh_token=refresh_token,
                access_expires_at=access_expires_at,
                refresh_expires_at=refresh_expires_at,
                username=username,
            )

        response.delete_cookie("refresh_token")
        response.delete_cookie("access_token")
        response.headers["Authorization"] = "Bearer " + "Hello, world!"
        return {"message": "Вы успешно вышли из системы"}
    except Exception as e:
        logger.error(f"Ошибка при выходе из системы: {str(e)}")
        return {"message": "Ошибка при выходе из системы"}
