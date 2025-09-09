import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import app_logger, setup_logging
from app.core.schemas import ErrorCode, ErrorResponse

# 设置日志
setup_logging()

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A FastAPI starter template for API projects",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    debug=settings.debug,
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # 记录请求信息
    app_logger.info(
        f"Request started: {request.method} {request.url}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "user_agent": request.headers.get("user-agent"),
            "client_ip": request.client.host,
        },
    )

    response = await call_next(request)

    # 记录响应信息
    process_time = time.time() - start_time
    app_logger.info(
        f"Request completed: {request.method} {request.url}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time,
        },
    )

    return response


# 全局异常处理
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    app_logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "url": str(request.url),
        },
    )

    error_response = ErrorResponse(
        error=ErrorCode.BAD_REQUEST,
        message=exc.detail,
        details={"status_code": exc.status_code},
    )

    return JSONResponse(
        status_code=exc.status_code, content=error_response.model_dump()
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    app_logger.warning(
        f"Validation Error: {exc.errors()}",
        extra={"errors": exc.errors(), "url": str(request.url)},
    )

    error_response = ErrorResponse(
        error=ErrorCode.VALIDATION_ERROR,
        message="Validation error",
        details={"errors": exc.errors()},
    )

    return JSONResponse(status_code=422, content=error_response.model_dump())


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    app_logger.error(
        f"Unhandled Exception: {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "url": str(request.url),
        },
    )

    error_response = ErrorResponse(
        error=ErrorCode.INTERNAL_ERROR,
        message="Internal server error",
        details={"exception_type": type(exc).__name__},
    )

    return JSONResponse(status_code=500, content=error_response.model_dump())


# 健康检查端点
@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


# 包含 API 路由
app.include_router(api_router, prefix="/api/v1")


# 根路径
@app.get("/", summary="API 信息")
async def root():
    """根路径，返回 API 基本信息"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs_url": "/api/v1/docs",
        "redoc_url": "/api/v1/redoc",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )
