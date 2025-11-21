from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy import func, text
from sqlalchemy.dialects import postgresql as pg
from sqlmodel import Field, Column, SQLModel


class BaseModelMixin(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
        ),
    )


class TimestampMixin:
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=False,
            onupdate=func.current_timestamp(),
        ),
    )
    

class SoftDeletedMixin:
    deleted_at: datetime | None = Field(
        default=None,
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )