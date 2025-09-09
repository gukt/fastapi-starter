"""Auth 模块的异常类"""

from typing import Any

from fastapi import HTTPException, status

from app.auth.constants import ErrorCode


class AuthException(HTTPException):
    """Auth 模块基础异常"""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": error_code.value,
                "message": message,
                "details": details or {},
            },
        )


class AuthenticationError(AuthException):
    """认证异常"""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            error_code=ErrorCode.AUTHENTICATION_ERROR,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class UserNotFoundError(AuthException):
    """用户未找到异常"""

    def __init__(
        self, message: str = "User not found", details: dict[str, Any] | None = None
    ):
        super().__init__(
            error_code=ErrorCode.USER_NOT_FOUND,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class UserAlreadyExistsError(AuthException):
    """用户已存在异常"""

    def __init__(
        self,
        message: str = "User already exists",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            error_code=ErrorCode.USER_ALREADY_EXISTS,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class InvalidCredentialsError(AuthException):
    """无效凭证异常"""

    def __init__(
        self,
        message: str = "Invalid credentials",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            error_code=ErrorCode.INVALID_CREDENTIALS,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class InsufficientPermissionsError(AuthException):
    """权限不足异常"""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class TokenExpiredError(AuthException):
    """Token 过期异常"""

    def __init__(
        self, message: str = "Token expired", details: dict[str, Any] | None = None
    ):
        super().__init__(
            error_code=ErrorCode.TOKEN_EXPIRED,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class TokenInvalidError(AuthException):
    """Token 无效异常"""

    def __init__(
        self, message: str = "Invalid token", details: dict[str, Any] | None = None
    ):
        super().__init__(
            error_code=ErrorCode.TOKEN_INVALID,
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )
