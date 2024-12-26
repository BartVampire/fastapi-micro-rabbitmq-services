import uuid as uuid_pkg

from pydantic import EmailStr
from sqlalchemy import String, LargeBinary, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base_model import BaseModel
from .mixins import IdIntPrimaryKeyMixin


class User(BaseModel, IdIntPrimaryKeyMixin):
    """
    Класс User представляет собой модель пользователя в базе данных. Он наследует от IdIntPrimaryKeyMixin и BaseModel.
    Поля класса:

    .username: Mapped[str] - Уникальное имя пользователя. Строка длиной до 50 символов. Поле индексируется для ускорения поиска.
    .email: Mapped[str] - Уникальный адрес электронной почты пользователя. Строка длиной до 50 символов. Поле индексируется для ускорения поиска.
    .phone_number: Mapped[str] - Уникальный номер телефона пользователя. Строка длиной до 25 символов. Поле индексируется для ускорения поиска.
    .hashed_password: Mapped[str] - Хэшированный пароль пользователя. Длина не ограничена.
    .uuid: Mapped[uuid_pkg.UUID] - Уникальный идентификатор пользователя в формате UUID. Генерируется автоматически с помощью uuid4.
    .is_active: Mapped[bool]- Логическое значение, указывающее, подтвержден ли пользователь. По умолчанию False. Поле индексируется для ускорения поиска.
    .is_superuser: Mapped[bool] - Логическое значение, указывающее, является ли пользователь суперпользователем. По умолчанию False.
    .tier_id: Mapped[int | None] - Идентификатор уровня доступа пользователя, который ссылается на другую таблицу tier. Это поле может быть None, если у пользователя нет уровня доступа. Поле индексируется для ускорения поиска.
    """

    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        default=uuid_pkg.uuid4, primary_key=False, unique=True
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(
        String(25), nullable=True, unique=True, index=True
    )
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary)
    is_active: Mapped[bool] = mapped_column(default=False, index=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    tier_id: Mapped[int | None] = mapped_column(
        Integer,
        index=True,
        default=None,
    )

    # active_tokens = relationship(
    #     "core.models.active_token_model.ActiveToken", back_populates="users"
    # )

    def __str__(self):
        return f'ID: "{self.id}" | Имя пользователя: "{self.username}" | Электронная почта: "{self.email}"'
