import uuid as uuid_pkg
from datetime import datetime, UTC, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import BaseModel  # относительный импорт
from core.mixins import IdIntPrimaryKeyMixin

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    # from services.user_service.core.models.restaurant_model import Restaurant


class User(BaseModel, IdIntPrimaryKeyMixin):
    """
    Класс User представляет собой модель пользователя в базе данных. Он наследует от IdIntPrimaryKeyMixin и BaseModel.
    Поля класса:

    .first_name: Mapped[str] - Имя пользователя. Строка длиной до 30 символов.
    .last_name: Mapped[str] - Фамилия пользователя. Строка длиной до 30 символов.
    .username: Mapped[str] - Уникальное имя пользователя. Строка длиной до 50 символов. Поле индексируется для ускорения поиска.
    .email: Mapped[str] - Уникальный адрес электронной почты пользователя. Строка длиной до 50 символов. Поле индексируется для ускорения поиска.
    .phone_number: Mapped[str] - Уникальный номер телефона пользователя. Строка длиной до 25 символов. Поле индексируется для ускорения поиска.
    .hashed_password: Mapped[str] - Хэшированный пароль пользователя. Длина не ограничена.
    .uuid: Mapped[uuid_pkg.UUID] - Уникальный идентификатор пользователя в формате UUID. Генерируется автоматически с помощью uuid4.
    .created_at: Mapped[datetime] - Дата и время создания записи пользователя. Устанавливается автоматически на текущее время в формате UTC при создании записи.
    .updated_at: Mapped[datetime | None] - Дата и время последнего обновления записи пользователя. По умолчанию None, что означает, что значение не установлено при создании.
    .deleted_at: Mapped[datetime | None] - Дата и время, когда запись была помечена как удаленная. По умолчанию None, что означает, что запись не удалена.
    .is_deleted: Mapped[bool] - Логическое значение, указывающее, была ли запись удалена. По умолчанию False. Поле индексируется для ускорения поиска удаленных записей.
    .is_active: Mapped[bool]- Логическое значение, указывающее, подтвержден ли пользователь. По умолчанию False. Поле индексируется для ускорения поиска.
    .is_superuser: Mapped[bool] - Логическое значение, указывающее, является ли пользователь суперпользователем. По умолчанию False.
    .tier_id: Mapped[int | None] - Идентификатор уровня доступа пользователя, который ссылается на другую таблицу tier. Это поле может быть None, если у пользователя нет уровня доступа. Поле индексируется для ускорения поиска.
    """

    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        default=uuid_pkg.uuid4, primary_key=False, unique=True
    )
    first_name: Mapped[str] = mapped_column(String(30), nullable=True)
    last_name: Mapped[str] = mapped_column(String(30), nullable=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(
        String(25), nullable=True, unique=True, index=True
    )
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=None,
        onupdate=lambda: datetime.now(timezone.utc),
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=False, index=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    tier_id: Mapped[int | None] = mapped_column(
        ForeignKey("tiers.id"),
        index=True,
        default=None,
    )

    tiers = relationship("core.models.tier_model.Tier", back_populates="users")
    # active_tokens = relationship(
    #     "app.core.models.active_token_model.ActiveToken", back_populates="users"
    # )
    # restaurants: Mapped[List["Restaurant"]] = relationship(
    #     "Restaurant", back_populates="owner"
    # )

    def __str__(self):
        return f'ID: "{self.id}" | Имя пользователя: "{self.username}" | Электронная почта: "{self.email}"'
