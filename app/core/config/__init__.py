"""配置模块

按领域分离的配置管理：
- app: 应用配置
- security: 安全配置
- database: 数据库配置
- redis: Redis配置
- cors: CORS配置
- logging: 日志配置
- files: 文件配置
"""

# 导出所有配置类供外部使用
from .app import AppConfig
from .cors import CorsConfig
from .database import DatabaseConfig
from .files import FileConfig
from .logging import LoggingConfig
from .redis import RedisConfig
from .security import SecurityConfig
from .settings import Settings, settings

__all__ = [
    "Settings",
    "settings",
    "AppConfig",
    "SecurityConfig",
    "DatabaseConfig",
    "RedisConfig",
    "CorsConfig",
    "LoggingConfig",
    "FileConfig",
]
