from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TokenBlackListCreate(BaseModel):
    """
    Схема для добавления токена в черный список:
    --- access_token: Токен доступа, который необходимо добавить в черный список.
    --- access_token_expires_at: Дата и время истечения срока действия токена доступа.
    --- refresh_token: Токен обновления, который необходимо добавить в черный список.
    --- refresh_token_expires_at: Дата и время истечения срока действия токена обновления.
    """

    access_token: str | bytes
    access_token_expires_at: datetime
    refresh_token: str | bytes = None
    refresh_token_expires_at: datetime

    class Config:
        orm_mode = True


class TokenBlackListRead(BaseModel):
    """
    Схема для чтения записи о токене в черном списке:
    --- uuid: Уникальный идентификатор записи.
    --- access_token: Токен доступа, который был добавлен в черный список.
    --- access_token_expires_at: Дата и время истечения срока действия токена доступа.
    --- refresh_token: Токен обновления, который был добавлен в черный список.
    --- refresh_token_expires_at: Дата и время истечения срока действия токена обновления.
    --- created_at: Дата и время создания записи.
    """

    uuid: UUID
    access_token: str | bytes = None
    access_token_expires_at: datetime
    refresh_token: str | bytes = None
    refresh_token_expires_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True


class TokenBlackListUpdate(BaseModel):
    """
    Схема для обновления записи о токене в черном списке:
    --- access_token: Токен доступа, который необходимо обновить в черном списке.
    --- access_token_expires_at: Дата и время истечения срока действия токена доступа.
    --- refresh_token: Токен обновления, который необходимо обновить в черном списке.
    --- refresh_token_expires_at: Дата и время истечения срока действия токена обновления.
    """

    access_token: str | bytes
    access_token_expires_at: datetime
    refresh_token: str | bytes = None
    refresh_token_expires_at: datetime = None

    class Config:
        orm_mode = True
