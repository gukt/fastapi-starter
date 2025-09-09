from pydantic import field_validator

from .base import BaseConfig


class CorsConfig(BaseConfig):
    """CORS 配置"""

    # 允许的主机
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "0.0.0.0"]

    # 允许的 HTTP 方法
    allowed_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

    # 允许的请求头
    allowed_headers: list[str] = ["*"]

    @field_validator("allowed_hosts", "allowed_methods", "allowed_headers", mode="before")
    @classmethod
    def parse_list(cls, v):
        """解析字符串列表"""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    class Config:
        env_prefix = "CORS_"
