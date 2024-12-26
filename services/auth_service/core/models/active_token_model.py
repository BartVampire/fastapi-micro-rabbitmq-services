import uuid as uuid_pkg
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, LargeBinary, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base_model import BaseModel


class ActiveToken(BaseModel):
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        default=uuid_pkg.uuid4, primary_key=True, unique=True
    )
    access_token: Mapped[bytes] = mapped_column(
        LargeBinary, unique=True, nullable=False, index=True
    )
    refresh_token: Mapped[bytes] = mapped_column(
        LargeBinary, unique=False, nullable=True, index=True
    )
    access_expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, unique=False
    )
    refresh_expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, unique=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    user_agent: Mapped[str] = mapped_column(String, nullable=True, unique=False)
    ip_address: Mapped[str] = mapped_column(String, nullable=True, unique=False)

    user_id: Mapped[int | None] = mapped_column(
        Integer, nullable=False, unique=False, index=True
    )
    #
    # # Связь с пользователем
    # users = relationship(
    #     "core.models.auth_user_model.User", back_populates="active_tokens"
    # )

    __table_args__ = {"extend_existing": True}
