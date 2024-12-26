from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from .base_schemas import TimestampSchema, UUIDSchema, PersistentDeletion


class UserSchema(BaseModel):
    """
    /// model_config = ConfigDict(strict=True): Устанавливает строгую проверку конфигурации, что означает, что любые
    дополнительные поля, не указанные в классе, вызовут ошибку валидации.
    /// first_name: Тип: str (строка). Ограничения: Минимальная длина: 2 символа, Максимальная длина: 30 символов, Примеры: "Иван", "Ivan".
    /// last_name: Тип: str (строка). Ограничения: Минимальная длина: 2 символа, Максимальная длина: 30 символов, Примеры: "Иванов", "Ivanov".
    /// username: Тип: str (строка). Ограничения: Минимальная длина: 3 символа, Максимальная длина: 50 символов
    Шаблон: должно содержать только латинские буквы (заглавные и строчные), цифры, символы подчеркивания и дефисы. Пример: "userName_777".
    /// email: Тип: EmailStr (строка с проверкой электронной почты). Ограничения: Минимальная длина: 4 символа, Максимальная длина: 50 символов. Пример: "ivanov@example.com".
    """

    # model_config = ConfigDict(strict=True)
    first_name: Annotated[
        str, Field(min_length=2, max_length=30, examples=["Иван", "Ivan"], default=None)
    ]
    last_name: Annotated[
        str,
        Field(min_length=2, max_length=30, examples=["Иванов", "Ivanov"], default=None),
    ]

    username: Annotated[
        str,
        Field(
            min_length=3,
            max_length=50,
            pattern=r"^[A-Za-z0-9_-]+$",
            examples=["userName_777"],
        ),
    ]
    email: Annotated[
        EmailStr | str, Field(min_length=4, max_length=50, examples=["ivanov@example.com"])
    ]
    phone_number: Annotated[
        str,
        Field(
            pattern=r"^\+\d{1,3}\d{4,14}$",  # Пример: +1234567890
            min_length=5,
            max_length=16,
            examples=["+79188888888", "+79288888888"],
        ),
    ]


class User(UserSchema, TimestampSchema, UUIDSchema, PersistentDeletion):
    """
    Схема для представления пользователя.

    Атрибуты:
    --- hashed_password (str): Хэшированный пароль пользователя.
    --- is_active (bool): Флаг, указывающий, активен ли пользователь.
    --- is_superuser (bool): Флаг, указывающий, является ли пользователь суперпользователем.
    --- tier_id (int | None): Идентификатор уровня доступа пользователя (опционально).
    """

    hashed_password: bytes
    is_active: bool
    is_superuser: bool = False
    tier_id: int | None = None


class UserRead(UserSchema):
    """
    Схема для чтения данных пользователя.

    Атрибуты:
    --- id (int): Уникальный идентификатор пользователя.
    --- tier_id (int | None): Идентификатор уровня доступа пользователя (опционально).
    """

    id: int
    tier_id: int | None


class UserCreate(UserSchema):
    """
    Схема для создания нового пользователя.

    Атрибуты:
    --- password (str): Пароль пользователя, который должен соответствовать определённым требованиям.
    """

    model_config = ConfigDict(extra="forbid")
    password: Annotated[
        str,
        Field(
            pattern=r"^.{8,}|[0-9]+|[A-Z]+|[a-z]+|[^a-zA-Z0-9]+$",
            examples=["Str3ngst!"],
        ),
    ]


class UserCreateInternal(UserSchema):
    """
    Схема для создания пользователя с внутренними данными.

    Атрибуты:
    --- hashed_password (str): Хэшированный пароль пользователя.
    """

    hashed_password: bytes


class UserUpdate(BaseModel):
    """
    Схема для обновления данных пользователя.

    Атрибуты:
    --- first_name (str | None): Имя пользователя (опционально).
    --- last_name (str | None): Фамилия пользователя (опционально).
    --- username (str | None): Уникальное имя пользователя (опционально).
    --- email (EmailStr | None): Адрес электронной почты пользователя (опционально).
    """

    model_config = ConfigDict(extra="forbid")

    first_name: Annotated[
        str, Field(min_length=2, max_length=30, examples=["Иван", "Ivan"], default=None)
    ]
    last_name: Annotated[
        str,
        Field(min_length=2, max_length=30, examples=["Иванов", "Ivanov"], default=None),
    ]

    email: Annotated[
        EmailStr,
        Field(
            min_length=4, max_length=50, examples=["ivanov@example.com"], default=None
        ),
    ]
    phone_number: Annotated[
        str,
        Field(
            pattern=r"^\+\d{1,3}\d{4,14}$",  # Пример: +1234567890
            min_length=5,
            max_length=16,
            examples=["+79188888888", "+79288888888"],
        ),
    ]


class UserUpdateInternal(UserUpdate):
    """
    Схема для обновления данных пользователя с внутренними метаданными.

    Атрибуты:
    --- updated_at (datetime): Дата и время последнего обновления.
    """

    updated_at: datetime


class UserTierUpdate(BaseModel):
    """
    Схема для обновления уровня доступа пользователя.

    Атрибуты:
    --- tier_id (int): Идентификатор нового уровня доступа пользователя.
    """

    tier_id: int


class UserDelete(BaseModel):
    """
    Схема для удаления пользователя.
    """


class UserRestoreDeleted(BaseModel):
    """
    Схема для восстановления удалённого пользователя.

    Атрибуты:
    --- is_deleted (bool): Флаг, указывающий, восстановлен ли пользователь.
    """

    is_deleted: bool
