from datetime import datetime

import jwt
from fastapi import Request, status, HTTPException, Depends

from api.auth_v1.auth_token_helpers import create_access_token
from api.auth_v1.token_crud import (
    is_token_blacklisted,
    add_tokens_to_db,
)
from api.auth_v1.validation_auth_helper_refresh import (
    get_current_auth_user_for_refresh,
)
from core.models.db_helper import db_helper
from auth_utils.utils_jwt import decode_jwt


async def check_and_refresh_token_dependency(
    request: Request,
    user=Depends(
        get_current_auth_user_for_refresh
    ),  # Получаем пользователя по refresh_token
):
    """
    Проверяет и обновляет токены, возвращая кортеж из request и актуального access_token
    """
    # Извлекаем токены из cookies
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    new_access_token = None

    # Получаем сессию БД
    async for db in db_helper.session_getter():

        # Проверка access_token
        if access_token:
            try:
                print(f"check_and_refresh_token_dependency: {access_token}")
                decode_jwt(access_token)
                # Токен действителен, возвращаем request для дальнейшего использования
                return request, access_token
            except jwt.ExpiredSignatureError:
                pass  # Токен истек, продолжаем проверку refresh_token

        # Проверка refresh_token и обновление access_token
        if (
            refresh_token
            and user
            and not await is_token_blacklisted(db=db, refresh_token=refresh_token)
        ):
            # Создаем новый access_token
            new_access_token = create_access_token(user=user)
            access_expires_at = datetime.fromtimestamp(
                decode_jwt(new_access_token).get("exp")
            )
            refresh_expires_at = datetime.fromtimestamp(
                decode_jwt(refresh_token).get("exp")
            )
            print(
                f"\n\n new_access_token: {new_access_token}\n\n refresh_token: {refresh_token}"
            )

            await add_tokens_to_db(
                db=db,
                user=user,
                access_token=new_access_token,
                access_expires_at=access_expires_at,
                refresh_token=refresh_token.encode("utf-8"),
                refresh_expires_at=refresh_expires_at,
                user_agent=request.headers.get("User-Agent"),
                ip_address=request.client.host,
            )

            # # Создаем ответ и добавляем новый access_token в cookie
            # response = Response()
            # response.set_cookie(
            #     key="access_token",
            #     value=access_token.decode("utf-8"),
            #     httponly=True,
            #     secure=True,  # Только для HTTPS
            #     samesite="strict",
            #     max_age=1800,  # Время жизни cookie (30 минут)
            # )
            request.state.token_data = (request, new_access_token)
            return request, new_access_token

        # Перенаправление на страницу авторизации, если токены отсутствуют или недействительны
    raise HTTPException(
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        detail="Необходима авторизация.",
    )
