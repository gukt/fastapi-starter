from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.auth.schemas import UserResponse


class PostBase(BaseModel):
    """文章基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    content: str = Field(..., min_length=1, description="内容")
    summary: str | None = Field(None, max_length=500, description="摘要")
    is_published: bool = Field(False, description="是否发布")


class PostCreate(PostBase):
    """创建文章模型"""
    slug: str = Field(..., min_length=1, max_length=200, description="URL 别名")


class PostUpdate(BaseModel):
    """更新文章模型"""
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1)
    summary: str | None = Field(None, max_length=500)
    is_published: bool | None = None
    slug: str | None = Field(None, min_length=1, max_length=200)


class PostResponse(PostBase):
    """文章响应模型"""
    id: UUID
    slug: str
    author_id: UUID
    created_at: datetime
    updated_at: datetime
    published_at: datetime | None = None
    author: UserResponse | None = None

    class Config:
        from_attributes = True


class TagBase(BaseModel):
    """标签基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    description: str | None = Field(None, max_length=500, description="描述")
    color: str | None = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="颜色代码")


class TagCreate(TagBase):
    """创建标签模型"""
    pass


class TagUpdate(BaseModel):
    """更新标签模型"""
    name: str | None = Field(None, min_length=1, max_length=50)
    description: str | None = Field(None, max_length=500)
    color: str | None = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class TagResponse(TagBase):
    """标签响应模型"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostWithTags(PostResponse):
    """带标签的文章响应模型"""
    tags: list[TagResponse] = Field([], description="标签列表")
