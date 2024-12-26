from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from .base_schemas import TimestampSchema


class TierBase(BaseModel):
    """
    Схема для представления базового уровня.

    Атрибуты:
    --- name (str): Название уровня, например, "free".
    """

    name: Annotated[str, Field(examples=["free"])]


class Tier(TimestampSchema, TierBase):
    """
    Схема для представления уровня с временными метками.

    Атрибуты:
    --- Наследует атрибуты от TierBase и TimestampSchema.
    """

    pass


class TierRead(TierBase):
    """
    Схема для чтения данных уровня.

    Атрибуты:
    --- id (int): Уникальный идентификатор уровня.
    --- created_at (datetime): Дата и время создания уровня.
    """

    id: int
    created_at: datetime


class TierCreate(TierBase):
    """
    Схема для создания нового уровня.

    Атрибуты:
    --- Наследует атрибуты от TierBase.
    """

    pass


class TierCreateInternal(TierCreate):
    """
    Схема для создания уровня с внутренними данными.

    Атрибуты:
    --- Наследует атрибуты от TierCreate.
    """

    pass


class TierUpdate(BaseModel):
    """
    Схема для обновления данных уровня.

    Атрибуты:
    --- name (str | None): Новое название уровня (опционально).
    """

    name: str | None = None


class TierUpdateInternal(TierUpdate):
    """
    Схема для обновления уровня с внутренними метаданными.

    Атрибуты:
    --- updated_at (datetime): Дата и время последнего обновления.
    """

    updated_at: datetime


class TierDelete(BaseModel):
    """
    Схема для удаления уровня.

    Атрибуты:
    --- Наследует атрибуты от BaseModel.
    """

    pass
