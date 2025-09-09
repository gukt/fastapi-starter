"""全局异常处理器模块"""

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.core.error import BaseAppError, ValidationError


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理程序"""

    @app.exception_handler(BaseAppError)
    async def app_error_handler(
        _request: Request,
        exc: BaseAppError,
    ):
        """处理自定义应用程序异常"""
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """处理 FastAPI 请求验证异常"""
        errors = []
        for error in exc.errors():
            error_info: dict[str, Any] = {
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"],
            }
            errors.append(error_info)

        validation_error = ValidationError(
            message="请求参数验证失败", details={"errors": errors}
        )

        return JSONResponse(
            status_code=validation_error.status_code, content=validation_error.to_dict()
        )

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_handler(
        _request: Request,
        exc: PydanticValidationError,
    ) -> JSONResponse:
        """处理 Pydantic 验证异常"""
        validation_error = ValidationError(
            message="数据验证失败",
            details={
                "errors": exc.errors(),
            },
        )
        return JSONResponse(
            status_code=validation_error.status_code,
            content=validation_error.to_dict(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """处理 FastAPI 的 HTTPException

        将标准 HTTPException 转换为统一错误响应格式
        """
        error = {
            "code": str(exc.status_code),
            "message": exc.detail,
        }

        headers = getattr(exc, "headers", None)
        if headers:
            error["details"] = {"headers": headers}

        return JSONResponse(
            status_code=exc.status_code,
            content={"error": error},
            headers=headers,
        )

    @app.exception_handler(Exception)
    async def uncaught_exception_handler(
        _request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """处理所有未分类的异常"""
        error = {
            "code": "internal_server_error",
            "message": "Internal Server Error",
            "details": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }

        return JSONResponse(
            status_code=500,
            content={"error": error},
        )
