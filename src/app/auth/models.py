
from datetime import datetime, timezone
from sqlmodel import Field, Column
from sqlalchemy.dialects import postgresql as pg
from core.domain.data_layers.model_mixins import TimestampMixin, SoftDeletedMixin, BaseModelMixin
from auth.schema import BaseUserSchema, RoleChoicesSchema

class User(BaseUserSchema, TimestampMixin, SoftDeletedMixin, BaseModelMixin, table=True):
    hashed_password: str = Field(max_length=256)
    failed_login_attempts: int = Field(default=0, ge=0, sa_type=pg.SMALLINT)
    last_failed_login: datetime | None = Field(
        default=None, 
        sa_column=Column(pg.TIMESTAMP(timezone=True))
    )
    otp: str = Field(max_length=6, default="")
    otp_expiry_at: datetime | None = Field(
        default=None, 
        sa_column=Column(pg.TIMESTAMP(timezone=True))
    )

    def has_role(self, role: RoleChoicesSchema) -> bool:
        return self.role.value == role.value