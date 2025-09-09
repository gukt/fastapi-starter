from .base import BaseConfig


class DatabaseConfig(BaseConfig):
    """数据库配置"""

    # 主数据库
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/fastapi_starter"

    # 测试数据库
    test_database_url: str = "postgresql+asyncpg://user:password@localhost:5432/fastapi_starter_test"

    class Config:
        env_prefix = "DATABASE_"
