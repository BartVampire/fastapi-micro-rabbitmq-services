import uuid as uuid_pkg
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_serializer


class HealthCheck(BaseModel):
    """
    Схема для проверки состояния сервиса.

    Атрибуты:
    --- name (str): Название сервиса.
    --- version (str): Версия сервиса.
    --- description (str): Описание сервиса.
    """

    name: str
    version: str
    description: str


# -------------- Миксины --------------
class UUIDSchema(BaseModel):
    """
    Схема для представления UUID.

    Атрибуты:
    --- uuid (UUID): Уникальный идентификатор, генерируемый автоматически.
    """

    uuid: uuid_pkg.UUID = Field(default_factory=uuid_pkg.uuid4)


class TimestampSchema(BaseModel):
    """
    Схема для представления временных меток.

    Атрибуты:
    --- created_at (datetime): Дата и время создания, генерируемые автоматически.
    --- updated_at (datetime): Дата и время последнего обновления.
    """

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default=None)

    @field_serializer("created_at")
    def serialize_dt(self, created_at: datetime | None, _info: Any) -> str | None:
        """
        Форматирует дату создания в строку формата ISO 8601. (YYYY-MM-DDTHH:MM:SSZ)
        """
        if created_at is not None:
            return created_at.isoformat()

        return None

    @field_serializer("updated_at")
    def serialize_updated_at(
        self, updated_at: datetime | None, _info: Any
    ) -> str | None:
        """
        Форматирует дату последнего обновления в строку формата ISO 8601. (YYYY-MM-DDTHH:MM:SSZ)
        """
        if updated_at is not None:
            return updated_at.isoformat()

        return None


class PersistentDeletion(BaseModel):
    """
    Схема для представления состояния удаления объекта.

    Атрибуты:
    --- deleted_at (datetime | None): Дата и время удаления, если объект удалён.
    --- is_deleted (bool): Флаг, указывающий, удалён ли объект.
    """

    deleted_at: datetime | None = Field(default=None)
    is_deleted: bool = False

    @field_serializer("deleted_at")
    def serialize_dates(self, deleted_at: datetime | None, _info: Any) -> str | None:
        """
        Форматирует дату удаления в строку формата ISO 8601. (YYYY-MM-DDTHH:MM:SSZ)
        """

        if deleted_at is not None:
            return deleted_at.isoformat()

        return None


# -------------- Токен --------------
class TokenInfo(BaseModel):
    access_token: str | bytes
    refresh_token: str | bytes = None
    token_type: str = "Bearer"
    access_expires_at: datetime  # Добавляем время истечения
    refresh_expires_at: datetime | None = None


class LogoutSchema(BaseModel):
    refresh_token: str | None = None


class Token(BaseModel):
    """
    Схема для представления токена доступа.

    Атрибуты:
    --- access_token (str): Токен доступа. (JWT)
    --- token_type (str): Тип токена (например, "Bearer").
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Схема для представления данных токена.

    Атрибуты:
    --- username_or_email (str): Имя пользователя или адрес электронной почты.
    """

    username_or_email: str


class TokenBlacklistBase(BaseModel):
    """
    Базовая схема для представления токена в черном списке.

    Атрибуты:
    --- token (str): Токен, который находится в черном списке.
    --- expires_at (datetime): Дата и время истечения срока действия токена.
    """

    token: str
    expires_at: datetime


class TokenBlacklistCreate(TokenBlacklistBase):
    """
    Схема для создания записи о токене в черном списке.
    Наследует от TokenBlacklistBase.
    """

    pass


class TokenBlacklistUpdate(TokenBlacklistBase):
    """
    Схема для обновления записи о токене в черном списке.
    Наследует от TokenBlacklistBase.
    """

    pass
