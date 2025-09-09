from .base import BaseConfig


class RedisConfig(BaseConfig):
    """Redis 配置"""

    # Redis 连接 URL
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_prefix = "REDIS_"
