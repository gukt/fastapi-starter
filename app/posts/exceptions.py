"""Posts 模块的异常类"""

from typing import Any

from fastapi import HTTPException, status

from app.posts.constants import ErrorCode


class PostException(HTTPException):
    """Posts 模块基础异常"""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": error_code.value,
                "message": message,
                "details": details or {}
            }
        )


class PostNotFoundError(PostException):
    """文章未找到异常"""

    def __init__(self, message: str = "Post not found", details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.POST_NOT_FOUND,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class PostAlreadyExistsError(PostException):
    """文章已存在异常"""

    def __init__(self, message: str = "Post already exists", details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.POST_ALREADY_EXISTS,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class SlugAlreadyExistsError(PostException):
    """Slug 已存在异常"""

    def __init__(self, message: str = "Slug already exists", details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.SLUG_ALREADY_EXISTS,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class AccessDeniedError(PostException):
    """访问被拒绝异常"""

    def __init__(self, message: str = "Access denied", details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.ACCESS_DENIED,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class NotAuthorError(PostException):
    """非作者异常"""

    def __init__(self, message: str = "You are not the author of this post", details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.NOT_AUTHOR,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class PostNotPublishedError(PostException):
    """文章未发布异常"""

    def __init__(self, message: str = "Post is not published", details: dict[str, Any] | None = None):
        super().__init__(
            error_code=ErrorCode.POST_NOT_PUBLISHED,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )
