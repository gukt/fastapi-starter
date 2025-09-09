from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.models import BaseModel


class Post(BaseModel):
    """文章模型"""
    __tablename__ = "posts"

    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    summary = Column(Text, nullable=True)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # 外键
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # 关系
    author = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title}, slug={self.slug})>"


class Tag(BaseModel):
    """标签模型"""
    __tablename__ = "tags"

    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # 十六进制颜色代码

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class PostTag(BaseModel):
    """文章标签关联模型"""
    __tablename__ = "post_tags"

    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id"), nullable=False)

    # 复合索引
    __table_args__ = (
        Index("ix_post_tags_post_tag", "post_id", "tag_id", unique=True),
    )
