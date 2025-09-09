from .base import BaseConfig


class SecurityConfig(BaseConfig):
    """安全配置"""

    # JWT 配置
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_prefix = "SECURITY_"
