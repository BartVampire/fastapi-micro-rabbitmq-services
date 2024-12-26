from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from core.models.active_token_model import ActiveToken
from core.models.token_blacklist_model import TokenBlackList
from core.schemas.auth_user_schemas import AuthUserSchema


async def add_tokens_to_db(
    db: AsyncSession,
    user: AuthUserSchema,
    access_token: bytes,
    access_expires_at: datetime,
    refresh_token: bytes | None = None,
    refresh_expires_at: datetime | None = None,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> ActiveToken:
    # Создаем запись об активных токенах
    token_record = ActiveToken(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        access_expires_at=access_expires_at,
        refresh_expires_at=refresh_expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    db.add(token_record)
    await db.commit()
    await db.refresh(token_record)
    return token_record


# Функция для добавления токенов в черный список
async def add_tokens_to_blacklist(
    db: AsyncSession,
    refresh_token: bytes | None = None,
    refresh_expires_at: datetime | None = None,
    username: str | None = None,
    access_expires_at: datetime | None = None,
    access_token: bytes | None = None,
):
    # Добавляем токены в черный список
    db_token_blacklist = TokenBlackList(
        refresh_token=refresh_token,
        refresh_expires_at=refresh_expires_at,
        username=username,
        access_token=access_token,
        access_expires_at=access_expires_at,
    )

    db.add(db_token_blacklist)
    await db.commit()
    await db.refresh(db_token_blacklist)

    return db_token_blacklist


async def is_token_blacklisted(
    db: AsyncSession,
    refresh_token: bytes | str = None,
    access_token: bytes | str = None,
) -> bool:
    if access_token:
        if type(access_token) is str:
            access_token = access_token.encode("utf-8")
        access_token_blacklist = await db.scalar(
            select(TokenBlackList).where(TokenBlackList.access_token == access_token)
        )

        if access_token_blacklist:
            return True
    if refresh_token:
        if type(refresh_token) is str:
            refresh_token = refresh_token.encode("utf-8")
    refresh_token_blacklist = await db.scalar(
        select(TokenBlackList).where(TokenBlackList.refresh_token == refresh_token)
    )

    if refresh_token_blacklist:
        return True

    return False


async def get_user_blacklisted_tokens(
    db: AsyncSession, username: str
) -> list[TokenBlackList]:
    token_black_lists = await db.scalars(
        select(TokenBlackList).where(TokenBlackList.username == username)
    )
    return list(token_black_lists)
