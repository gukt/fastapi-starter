import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging

# 设置日志
setup_logging()
logger = logging.getLogger("app")

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app.app_name,
    version=settings.app.app_version,
    description="A FastAPI starter template for API projects",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    debug=settings.debug,
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allowed_hosts,
    allow_credentials=True,
    allow_methods=settings.cors.allowed_methods,
    allow_headers=settings.cors.allowed_headers,
)

# 注册全局异常处理器
register_exception_handlers(app)

# 包含 API 路由
app.include_router(api_router, prefix="/api/v1")


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # 记录请求信息
    logger.info(
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
    logger.info(
        f"Request completed: {request.method} {request.url}",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time,
        },
    )

    return response


# 健康检查端点
@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


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
