import logging
import sys

from loguru import logger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """拦截标准日志处理器"""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """设置日志配置"""
    # 移除默认的日志处理器
    logger.remove()

    # 添加控制台日志处理器
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # 添加文件日志处理器（仅在生产环境）
    if settings.is_production:
        logger.add(
            "logs/app.log",
            rotation="10 MB",
            retention="30 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level=settings.log_level,
            compression="zip",
        )

    # 添加错误日志文件
    logger.add(
        "logs/error.log",
        rotation="10 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        compression="zip",
    )

    # 拦截标准库的日志
    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=settings.log_level,
        force=True,
    )

    # 设置第三方库的日志级别
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "sqlalchemy", "redis"]:
        logging_logger = logging.getLogger(logger_name)
        if logger_name == "uvicorn.access":
            logging_logger.handlers = [InterceptHandler()]
            logging_logger.setLevel(logging.INFO)
        else:
            logging_logger.handlers = [InterceptHandler()]
            logging_logger.setLevel(settings.log_level)


def get_logger(name: str):
    """获取指定名称的日志器"""
    return logger.bind(name=name)
