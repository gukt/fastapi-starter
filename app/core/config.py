from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    app_name: str = "fastapi-starter"
    app_version: str = "0.1.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    environment: str = "development"

    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Database
    database_url: str = (
        "postgresql+asyncpg://user:password@localhost:5432/fastapi_starter"
    )
    test_database_url: str = (
        "postgresql+asyncpg://user:password@localhost:5432/fastapi_starter_test"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # CORS
    allowed_hosts: list[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    allowed_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    allowed_headers: list[str] = ["*"]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # File upload
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "uploads"

    @field_validator(
        "allowed_hosts", "allowed_methods", "allowed_headers", mode="before"
    )
    @classmethod
    def parse_list(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

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
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"


settings = Settings()
