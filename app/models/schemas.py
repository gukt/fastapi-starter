from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr = Field(..., description="用户邮箱")
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")


class UserCreate(UserBase):
    """创建用户模型"""
    password: str = Field(..., min_length=8, description="密码")
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含数字')
        return v


class UserUpdate(BaseModel):
    """更新用户模型"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应模型"""
    id: UUID
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模型"""
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """令牌模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: Optional[UUID] = None
    username: Optional[str] = None


class PostBase(BaseModel):
    """文章基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    content: str = Field(..., min_length=1, description="内容")
    summary: Optional[str] = Field(None, max_length=500, description="摘要")
    is_published: bool = Field(False, description="是否发布")


class PostCreate(PostBase):
    """创建文章模型"""
    slug: str = Field(..., min_length=1, max_length=200, description="URL别名")


class PostUpdate(BaseModel):
    """更新文章模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    is_published: Optional[bool] = None
    slug: Optional[str] = Field(None, min_length=1, max_length=200)


class PostResponse(PostBase):
    """文章响应模型"""
    id: UUID
    slug: str
    author_id: UUID
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    author: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True


class TagBase(BaseModel):
    """标签基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$", description="颜色代码")


class TagCreate(TagBase):
    """创建标签模型"""
    pass


class TagUpdate(BaseModel):
    """更新标签模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, regex="^#[0-9A-Fa-f]{6}$")


class TagResponse(TagBase):
    """标签响应模型"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PostWithTags(PostResponse):
    """带标签的文章响应模型"""
    tags: List[TagResponse] = Field([], description="标签列表")