from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """错误代码枚举"""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    BAD_REQUEST = "BAD_REQUEST"


class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    data: Any | None = Field(None, description="响应数据")
    success: bool = Field(True, description="请求是否成功")
    message: str | None = Field(None, description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")


class ErrorResponse(BaseModel):
    """错误响应格式"""
    error: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    details: dict[str, Any] | None = Field(None, description="错误详细信息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="错误时间戳")


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页大小")


class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    total: int = Field(..., description="总记录数")
    pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class PaginatedResponse(ApiResponse):
    """分页响应"""
    data: list = Field(..., description="数据列表")
    meta: PaginationMeta = Field(..., description="分页元数据")


class SortParams(BaseModel):
    """排序参数"""
    sort_by: str | None = Field(None, description="排序字段")
    sort_order: str | None = Field("asc", pattern="^(asc|desc)$", description="排序方向")


class FilterParams(BaseModel):
    """过滤参数基类"""
    pass
