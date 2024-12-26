import uuid as uuid_pkg
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, LargeBinary
from sqlalchemy.orm import mapped_column, Mapped

from core.models import BaseModel


class TokenBlackList(BaseModel):
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        default=uuid_pkg.uuid4, primary_key=True, unique=True
    )
    access_token: Mapped[bytes | None] = mapped_column(
        LargeBinary, unique=True, index=True, nullable=False
    )
    access_expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, unique=False
    )
    refresh_token: Mapped[bytes] = mapped_column(
        LargeBinary,
        unique=False,
        index=True,
        nullable=True,
    )
    refresh_expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True, unique=False
    )
    username: Mapped[str] = mapped_column(
        String(50), index=True, nullable=True, unique=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = {"extend_existing": True}
