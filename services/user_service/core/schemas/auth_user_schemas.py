from typing import Annotated, Optional

from pydantic import BaseModel, Field, EmailStr


class AuthUserSchema(BaseModel):
    """Схема для пользователя"""
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
        ),]
    hashed_password: bytes | str
    is_active: bool
    is_superuser: bool
    tier_id: Optional[int]