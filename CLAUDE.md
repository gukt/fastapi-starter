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
from app.core.auth import get_current_active_user
current_user: User = Depends(get_current_active_user)

# Admin-only endpoints
from app.core.auth import get_current_superuser
admin_user: User = Depends(get_current_superuser)

# JWT token handling in @app/core/auth.py
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

-   Routes organized by version in @app/api/v1/
-   Each feature has its own router file (auth.py, posts.py, etc.)
-   All routers registered in @app/api/v1/**init**.py
-   Automatic OpenAPI documentation generation

## File Structure (Developer View)

```
app/
├── api/v1/               # API routers
│   ├── auth.py           # Authentication endpoints
│   ├── posts.py          # Post management endpoints
│   └── __init__.py       # Router registration
├── core/                 # Core infrastructure
│   ├── auth.py           # JWT authentication
│   ├── config.py         # Settings management
│   ├── decorators.py     # Response decorators
│   ├── logging.py        # Loguru logging setup
│   ├── redis.py          # Redis cache management
│   └── schemas.py        # Base response schemas
├── database/             # Database layer
│   └── session.py        # Async session management
├── models/               # Data models
│   ├── models.py         # SQLAlchemy models
│   └── schemas.py        # Pydantic schemas
├── utils/                # Utilities
│   └── pagination.py     # Pagination helpers
└── main.py               # FastAPI application with middleware
```

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

### Adding New API Endpoint

```python
# 1. Create schema in @app/models/schemas.py
class NewItemSchema(BaseModel):
    name: str = Field(..., min_length=1)

# 2. Create model in @app/models/models.py
class NewItem(BaseModel):
    name = Column(String(100), nullable=False)

# 3. Add router in @app/api/v1/
@router.post("/items")
@handle_response("Item created successfully")
async def create_item(
    item_data: NewItemSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    new_item = NewItem(**item_data.model_dump())
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item

# 4. Register router in @app/api/v1/__init__.py
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
