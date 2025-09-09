import traceback
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any

from fastapi import HTTPException, status

from app.core.logging import api_logger
from app.core.schemas import ApiResponse, ErrorCode, ErrorResponse


def handle_response(
    success_message: str | None = None,
    error_code: str | None = None,
    include_data: bool = True,
    cache_key: str | None = None,
    cache_timeout: int | None = None
):
    """
    统一响应格式装饰器
    
    Args:
        success_message: 成功时的消息
        error_code: 错误代码
        include_data: 是否包含数据
        cache_key: 缓存键
        cache_timeout: 缓存超时时间
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # 执行原函数
                result = await func(*args, **kwargs)

                # 处理响应
                if include_data:
                    response_data = {"data": result}
                else:
                    response_data = {}

                if success_message:
                    response_data["message"] = success_message

                response = ApiResponse(**response_data)
                api_logger.info(f"API success: {func.__name__}", extra={
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                })

                return response

            except HTTPException as e:
                # 处理HTTP异常
                error_response = ErrorResponse(
                    error=error_code or ErrorCode.BAD_REQUEST,
                    message=e.detail,
                    details={"status_code": e.status_code}
                )
                api_logger.warning(f"HTTP Exception: {func.__name__} - {e.detail}", extra={
                    "function": func.__name__,
                    "status_code": e.status_code,
                    "detail": e.detail
                })
                raise HTTPException(
                    status_code=e.status_code,
                    detail=error_response.model_dump()
                )

            except ValueError as e:
                # 处理值错误
                error_response = ErrorResponse(
                    error=ErrorCode.VALIDATION_ERROR,
                    message=str(e),
                    details={"function": func.__name__}
                )
                api_logger.warning(f"Validation error: {func.__name__} - {str(e)}", extra={
                    "function": func.__name__,
                    "error": str(e)
                })
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=error_response.model_dump()
                )

            except Exception as e:
                # 处理其他异常
                error_response = ErrorResponse(
                    error=ErrorCode.INTERNAL_ERROR,
                    message="Internal server error",
                    details={
                        "function": func.__name__,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "traceback": traceback.format_exc() if not error_code else None
                    }
                )
                api_logger.error(f"Internal error: {func.__name__} - {str(e)}", extra={
                    "function": func.__name__,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                })
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_response.model_dump()
                )

        return wrapper
    return decorator


def handle_exceptions(error_code: str | None = None):
    """
    异常处理装饰器
    
    Args:
        error_code: 错误代码
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except ValueError as e:
                error_response = ErrorResponse(
                    error=error_code or ErrorCode.VALIDATION_ERROR,
                    message=str(e),
                    details={"function": func.__name__}
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=error_response.model_dump()
                )
            except Exception as e:
                error_response = ErrorResponse(
                    error=error_code or ErrorCode.INTERNAL_ERROR,
                    message="Internal server error",
                    details={
                        "function": func.__name__,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "traceback": traceback.format_exc()
                    }
                )
                api_logger.error(f"Internal error: {func.__name__} - {str(e)}", extra={
                    "function": func.__name__,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                })
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_response.model_dump()
                )

        return wrapper
    return decorator


class ResponseHandler:
    """响应处理器"""

    @staticmethod
    def success(
        data: Any = None,
        message: str | None = None,
        status_code: int = status.HTTP_200_OK
    ) -> dict[str, Any]:
        """成功响应"""
        response = {
            "data": data,
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow()
        }
        return response, status_code

    @staticmethod
    def error(
        error: str,
        message: str,
        details: dict[str, Any] | None = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ) -> dict[str, Any]:
        """错误响应"""
        response = ErrorResponse(
            error=error,
            message=message,
            details=details
        )
        return response.model_dump(), status_code

    @staticmethod
    def validation_error(
        message: str,
        details: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """验证错误响应"""
        return ResponseHandler.error(
            error=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    @staticmethod
    def not_found(
        message: str = "Resource not found",
        details: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """未找到响应"""
        return ResponseHandler.error(
            error=ErrorCode.NOT_FOUND,
            message=message,
            details=details,
            status_code=status.HTTP_404_NOT_FOUND
        )

    @staticmethod
    def unauthorized(
        message: str = "Unauthorized",
        details: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """未授权响应"""
        return ResponseHandler.error(
            error=ErrorCode.AUTHENTICATION_ERROR,
            message=message,
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    @staticmethod
    def forbidden(
        message: str = "Forbidden",
        details: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """禁止访问响应"""
        return ResponseHandler.error(
            error=ErrorCode.AUTHORIZATION_ERROR,
            message=message,
            details=details,
            status_code=status.HTTP_403_FORBIDDEN
        )
