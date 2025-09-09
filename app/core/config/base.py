from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    """基础配置类，包含通用的配置逻辑"""

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"
        extra = "ignore"
