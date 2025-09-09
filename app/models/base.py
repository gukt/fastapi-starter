import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import expression

from app.database.session import Base


class BaseModel(Base):
    """基础模型类"""

    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class SoftDeletableModel:
    """软删除模型基类"""

    __abstract__ = True

    deleted_at = Column(
        DateTime(timezone=True), nullable=True, index=True, comment="删除时间"
    )
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        server_default=expression.false(),
        comment="是否已删除",
    )

    def delete(self):
        """软删除实例"""
        self.updated_at = datetime.now(UTC)
        self.deleted_at = datetime.now(UTC)
        self.is_deleted = True

    def restore(self):
        """恢复软删除的实例"""
        self.updated_at = datetime.now(UTC)
        self.deleted_at = None
        self.is_deleted = False

    @property
    def is_active_deleted(self):
        """检查实例是否被软删除"""
        return self.is_deleted or self.deleted_at is not None


class AuditableModel:
    """时间戳模型基类"""

    __abstract__ = True

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True, comment="更新时间"
    )

    def touch(self):
        """手动更新 updated_at 时间戳"""
        self.updated_at = datetime.now(UTC)
