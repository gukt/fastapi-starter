from .app import AppConfig
from .cors import CorsConfig
from .database import DatabaseConfig
from .files import FileConfig
from .logging import LoggingConfig
from .redis import RedisConfig
from .security import SecurityConfig


class Settings:
    """配置聚合器，统一管理所有配置"""

    def __init__(self):
        # 每个配置类独立加载，避免环境变量冲突
        self.app = AppConfig(_env_file=".env")
        self.security = SecurityConfig(_env_file=".env")
        self.database = DatabaseConfig(_env_file=".env")
        self.redis = RedisConfig(_env_file=".env")
        self.cors = CorsConfig(_env_file=".env")
        self.logging = LoggingConfig(_env_file=".env")
        self.files = FileConfig(_env_file=".env")

    # 为了向后兼容，提供一些属性的直接访问
    @property
    def app_name(self) -> str:
        return self.app.app_name

    @property
    def app_version(self) -> str:
        return self.app.app_version

    @property
    def debug(self) -> bool:
        return self.app.debug

    @property
    def environment(self) -> str:
        return self.app.environment

    @property
    def is_production(self) -> bool:
        return self.app.is_production

    @property
    def is_development(self) -> bool:
        return self.app.is_development

    @property
    def is_testing(self) -> bool:
        return self.app.is_testing

    @property
    def secret_key(self) -> str:
        return self.security.secret_key

    @property
    def algorithm(self) -> str:
        return self.security.algorithm

    @property
    def access_token_expire_minutes(self) -> int:
        return self.security.access_token_expire_minutes

    @property
    def database_url(self) -> str:
        return self.database.database_url

    @property
    def test_database_url(self) -> str:
        return self.database.test_database_url

    @property
    def redis_url(self) -> str:
        return self.redis.redis_url

    @property
    def allowed_hosts(self) -> list[str]:
        return self.cors.allowed_hosts

    @property
    def allowed_methods(self) -> list[str]:
        return self.cors.allowed_methods

    @property
    def allowed_headers(self) -> list[str]:
        return self.cors.allowed_headers

    @property
    def log_level(self) -> str:
        return self.logging.log_level

    @property
    def log_format(self) -> str:
        return self.logging.log_format

    @property
    def max_file_size(self) -> int:
        return self.files.max_file_size

    @property
    def upload_dir(self) -> str:
        return self.files.upload_dir

    @property
    def rate_limit_requests(self) -> int:
        return self.app.rate_limit_requests

    @property
    def rate_limit_window(self) -> int:
        return self.app.rate_limit_window

    @property
    def app_host(self) -> str:
        return self.app.app_host

    @property
    def app_port(self) -> int:
        return self.app.app_port


# 全局配置实例
settings = Settings()
