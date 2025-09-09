from typing import Literal

from .base import BaseConfig


class LoggingConfig(BaseConfig):
    """日志配置"""

    # 日志级别
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # 日志格式
    log_format: Literal["json", "text"] = "json"

    class Config:
        env_prefix = "LOGGING_"
