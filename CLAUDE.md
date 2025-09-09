# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

此文件为 Claude Code 在此仓库中工作时提供指导，确保代码质量和一致性。

## 全局规范

-   文件编码: 确保所有文件使用 UTF-8 编码，避免中文乱码
-   排版格式: 中文与英文/数字之间添加空格
-   回复语言: 默认使用中文回复（除非特殊说明）

## Quick Overview

See @README.md for complete project overview, setup instructions, and API documentation.

## Development Commands

### Environment Setup

```bash
# One-time setup (recommended)
./dev.sh setup

# Manual dependency management
uv sync                    # Install all dependencies
uv sync --group dev        # Install development dependencies only
```

### Development Workflow

```bash
# Start development environment
./dev.sh dev               # Development server with hot reload
./dev.sh docker-dev        # Full Docker environment (postgres + redis + app)

# Code quality
./dev.sh format            # Format code with Ruff
./dev.sh typecheck         # Type checking with MyPy
./dev.sh test              # Run tests with coverage

# Database operations
./dev.sh superuser         # Create admin user
./dev.sh clean             # Clean cache and build files

# Production
./dev.sh prod              # Production server
./dev.sh docker-prod       # Docker production deployment
```

### Manual Commands

```bash
# Direct uvicorn usage
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing specific files
uv run pytest tests/test_auth.py -v
uv run pytest --cov=app --cov-report=html

# Database operations
uv run python -c "from app.database.session import create_tables; import asyncio; asyncio.run(create_tables())"
```

## Key Development Patterns

### Response Format

-   Always use `@handle_response()` decorator for API endpoints
-   Success responses automatically wrapped: `{"data": ...}`
-   Error responses automatically formatted: `{"error": "CODE", "message": "...", "details": {optional-dict}}`
-   See @app/core/decorators.py for implementation details

### Authentication & Authorization

```python
# Basic authentication
from app.auth.dependencies import get_current_active_user
current_user: User = Depends(get_current_active_user)

# Admin-only endpoints
from app.auth.dependencies import get_current_superuser
admin_user: User = Depends(get_current_superuser)

# JWT token handling in @app/auth/service.py
```

### Database Operations

```python
# Database sessions
from app.database.session import get_db
db: AsyncSession = Depends(get_db)

# Models inherit from BaseModel
from app.models.models import BaseModel
class MyModel(BaseModel):
    # UUID primary key, timestamps, and soft delete included

# Domain-specific models
from app.auth.models import User
from app.posts.models import Post
```

### Pagination

```python
# Use utility for consistent pagination
from app.utils.pagination import get_paginated_results
result = await get_paginated_results(
    session=db,
    model=MyModel,
    page=page,
    size=size,
    search_term=search,
    sort_by=sort_by,
    sort_order=sort_order
)
```

### API Structure

-   **Simplified Domain-Driven Design**: Each domain is a flat module with 7 core files
-   **Clear separation**: Models, schemas, service, router, dependencies, constants, exceptions
-   **Unified routing**: All routers registered in @app/api/v1/__init__.py
-   **Automatic documentation**: OpenAPI/Swagger docs generated automatically
-   **Consistent patterns**: Same structure across all domains for maintainability

## File Structure (Developer View)

```
app/
├── auth/                 # 认证领域模块 (7 个核心文件)
│   ├── models.py         # SQLAlchemy 用户模型
│   ├── schemas.py        # Pydantic 认证模式
│   ├── service.py        # 认证业务逻辑
│   ├── router.py         # 认证 API 路由
│   ├── dependencies.py   # 认证依赖注入
│   ├── constants.py      # 认证常量定义
│   └── exceptions.py     # 认证异常类
├── posts/                # 文章领域模块 (7 个核心文件)
│   ├── models.py         # SQLAlchemy 文章模型
│   ├── schemas.py        # Pydantic 文章模式
│   ├── service.py        # 文章业务逻辑
│   ├── router.py         # 文章 API 路由
│   ├── dependencies.py   # 文章依赖注入
│   ├── constants.py      # 文章常量定义
│   └── exceptions.py     # 文章异常类
├── api/v1/               # API 路由注册
│   └── __init__.py       # 统一路由注册
├── core/                 # 核心基础设施
│   ├── auth.py           # JWT 认证服务
│   ├── config.py         # 配置管理
│   ├── decorators.py     # 响应装饰器
│   ├── logging.py        # 日志配置
│   ├── redis.py          # Redis 缓存
│   └── schemas.py        # 基础响应模式
├── models/               # 共享数据模型
│   └── models.py         # 基础模型类和审计日志
├── database/             # 数据库层
│   └── session.py        # 异步会话管理
├── utils/                # 工具类
│   └── pagination.py     # 分页助手
└── main.py               # FastAPI 应用入口
```

### Architecture Benefits

- **Simplified structure**: Reduced from 17+ files per domain to 7 essential files
- **Better maintainability**: Flat structure is easier to navigate and understand
- **Consistent patterns**: Same structure across all domains
- **Domain-driven**: Clear separation of business concerns
- **FastAPI optimized**: Leverages FastAPI's strengths (dependency injection, type safety)

## Configuration

### Environment Variables

-   Copy @.env.example to `.env` and configure
-   Key settings: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `ENVIRONMENT`
-   See @app/core/config.py for all available settings

### Dependencies

-   Runtime dependencies in @pyproject.toml `[project.dependencies]`
-   Development tools in @pyproject.toml `[project.optional-dependencies.dev]`
-   Use `uv add <package>` for new dependencies
-   Use `uv add --group dev <package>` for dev dependencies

### Docker Services

-   PostgreSQL: `docker compose up postgres`
-   Redis: `docker compose up redis`
-   Full environment: `./dev.sh docker-dev`
-   See @docker-compose.yml for service configurations

## Testing

### Test Structure

-   Unit tests in @tests/unit/ (not yet implemented)
-   Integration tests in @tests/integration/ (not yet implemented)
-   Test fixtures in @tests/conftest.py
-   Use `pytest-asyncio` for async tests

### Running Tests

```bash
# All tests
./dev.sh test

# With coverage
uv run pytest --cov=app --cov-report=html --cov-report=term

# Specific test categories
uv run pytest tests/test_auth.py -v
uv run pytest -k "test_auth_" -v
```

## Common Development Tasks

### Adding New Domain Module

```python
# 1. Create new domain directory with 7 core files
app/new_domain/
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic schemas
├── service.py        # Business logic
├── router.py         # API routes
├── dependencies.py   # Dependency injection
├── constants.py      # Constants
└── exceptions.py     # Custom exceptions

# 2. Register router in @app/api/v1/__init__.py
from app.new_domain.router import router as new_domain_router
api_router.include_router(new_domain_router)
```

### Adding New API Endpoint (in existing domain)

```python
# 1. Add schema in @app/{domain}/schemas.py
class NewItemSchema(BaseModel):
    name: str = Field(..., min_length=1)

# 2. Add model in @app/{domain}/models.py
class NewItem(BaseModel):
    name = Column(String(100), nullable=False)

# 3. Add business logic in @app/{domain}/service.py
class DomainService:
    @staticmethod
    async def create_item(db: AsyncSession, item_data: NewItemSchema):
        new_item = NewItem(**item_data.model_dump())
        db.add(new_item)
        await db.commit()
        await db.refresh(new_item)
        return new_item

# 4. Add route in @app/{domain}/router.py
@router.post("/items")
@handle_response("Item created successfully")
async def create_item(
    item_data: NewItemSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return await DomainService.create_item(db, item_data)
```

### Adding Authentication

```python
# Protect endpoints
@router.get("/protected")
@handle_response()
async def protected_route(
    current_user: User = Depends(get_current_active_user)
):
    return {"data": current_user}

# Admin-only endpoints
@router.delete("/admin-only")
@handle_response()
async def admin_route(
    current_user: User = Depends(get_current_superuser)
):
    return {"data": "Admin operation completed"}
```

### Working with Redis

```python
from app.core.redis import redis_cache

# Cache operations
await redis_cache.set("key", value, timeout=3600)
cached_value = await redis_cache.get("key")
await redis_cache.delete("key")

# Cache key generation
from app.core.redis import CacheKeyBuilder
key = CacheKeyBuilder.user_cache_key(user_id)
```

### Error Handling

```python
# Custom error responses
from app.core.decorators import handle_exceptions

@handle_exceptions("CUSTOM_ERROR")
async def risky_operation():
    # Will automatically return formatted error response
    raise ValueError("Something went wrong")

# HTTP exceptions
raise HTTPException(
    status_code=400,
    detail={"error": "VALIDATION_ERROR", "message": "Invalid input"}
)
```

## Debugging

### Logging

-   Colored logs automatically configured in @app/core/logging.py
-   Use `app_logger`, `api_logger`, `db_logger`, etc. for context-specific logging
-   Logs written to both console and @logs/ directory

### Common Issues

-   Database connection: Ensure PostgreSQL is running and `DATABASE_URL` is correct
-   Redis connection: Ensure Redis is running and `REDIS_URL` is correct
-   JWT errors: Check `SECRET_KEY` configuration
-   Import errors: Run `uv sync` to install dependencies

## Code Quality

### Formatting & Linting

-   Ruff handles both formatting and linting
-   Configuration in @pyproject.toml `[tool.ruff]`
-   Pre-commit hooks in @.pre-commit-config.yaml
-   Run `./dev.sh format` to fix all auto-fixable issues

### Type Checking

-   MyPy configuration in @pyproject.toml `[tool.mypy]`
-   100% type annotation coverage required
-   Run `./dev.sh typecheck` to verify

### Git Workflow

-   Pre-commit hooks automatically run on commit
-   Manual pre-commit run: `uv run pre-commit run --all-files`
-   See @.pre-commit-config.yaml for configured hooks

## Project Architecture Guidelines

### Key Principles

1. **Domain-Driven Design (DDD)**: Organize code by business domains, not technical layers
2. **Simplified Structure**: Avoid over-engineering - use flat modules with essential files only
3. **Consistent Patterns**: Each domain follows the same 7-file structure
4. **Clear Responsibilities**: Separate concerns between models, services, and routes
5. **FastAPI Best Practices**: Leverage dependency injection, type safety, and async patterns

### When to Use This Structure

- **Small to medium projects**: Perfect for teams up to 10 developers
- **Startups and MVPs**: Quick development with clear structure
- **Domain-focused applications**: When business domains are well-defined
- **FastAPI projects**: Optimized for FastAPI's strengths

### When to Consider More Complex Structure

- **Large enterprise applications**: Multiple teams working on different domains
- **Microservices architecture**: When each domain becomes a separate service
- **Complex business logic**: When domains have intricate internal structures
- **Long-term maintenance**: When the project will be maintained for many years

### Refactoring Guidelines

- **Start simple**: Begin with the simplified structure
- **Evolve as needed**: Add complexity only when justified by requirements
- **Maintain consistency**: Keep the same patterns across all domains
- **Document decisions**: Record architectural decisions in @docs/ directory

### Migration from Traditional Structure

If migrating from a traditional FastAPI structure:

1. **Identify domains**: Group related functionality by business domain
2. **Create domain modules**: Move domain-specific code to dedicated modules
3. **Update imports**: Change all import paths to use new domain structure
4. **Test thoroughly**: Ensure all functionality works after migration
5. **Update documentation**: Reflect new structure in README and developer docs

### Performance Considerations

- **Lazy imports**: Use lazy imports to reduce startup time
- **Database connections**: Use connection pooling and async operations
- **Caching**: Implement Redis caching for frequently accessed data
- **Pagination**: Always use pagination for large datasets
- **Background tasks**: Use Celery or FastAPI background tasks for long-running operations

### Security Best Practices

- **JWT tokens**: Use secure token handling and expiration
- **Input validation**: Validate all inputs with Pydantic schemas
- **SQL injection prevention**: Use SQLAlchemy ORM instead of raw SQL
- **CORS**: Configure CORS properly for your frontend
- **Environment variables**: Never commit secrets to version control
