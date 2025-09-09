from typing import Literal

from pydantic import field_validator

from .base import BaseConfig


class AppConfig(BaseConfig):
    """应用配置"""

    # 应用基本信息
    app_name: str = "fastapi-starter"
    app_version: str = "0.1.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # 环境配置
    debug: bool = False
    environment: Literal["development", "production", "testing"] = "development"

    # 限流配置
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    @field_validator('debug', mode='before')
    @classmethod
    def parse_bool(cls, v):
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return bool(v)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"

    class Config:
        env_prefix = "APP_"
