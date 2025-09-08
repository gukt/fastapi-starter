# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a complete FastAPI starter template with modern tooling and best practices. The project includes authentication, database management, Redis caching, unified response format, and comprehensive development tools.

## Development Commands

### Environment Setup

```bash
# Use the development script (recommended)
./dev.sh setup

# Manual setup with uv
uv sync
```

### Running the Application

```bash
# Development server with hot reload
./dev.sh dev

# Production server
./dev.sh prod

# Using uvicorn directly
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Development Tools

```bash
# All-in-one development script
./dev.sh setup          # Setup environment
./dev.sh install        # Install dependencies
./dev.sh test           # Run tests
./dev.sh format         # Format code with Ruff
./dev.sh typecheck      # Type checking with MyPy
./dev.sh superuser      # Create superuser
./dev.sh clean          # Clean cache files

# Docker environments
./dev.sh docker-dev     # Docker development environment
./dev.sh docker-prod    # Docker production environment
```

## Project Structure

```
fastapi-starter/
├── app/
│   ├── api/v1/          # API routers (auth, posts, etc.)
│   ├── core/            # Core modules (auth, config, decorators, logging, redis)
│   ├── database/        # Database session management
│   ├── models/          # SQLAlchemy models and Pydantic schemas
│   ├── utils/           # Utilities (pagination, etc.)
│   └── main.py          # FastAPI application entry point
├── tests/               # Test files with fixtures
├── docs/                # Documentation
├── logs/                # Application logs
├── docker-compose.yml   # Docker services configuration
├── pyproject.toml      # Project configuration and dependencies
├── .env.example        # Environment variables template
└── dev.sh             # Development helper script
```

## Key Patterns

### Response Format
- Use `@handle_response()` decorator for automatic response wrapping
- Success responses: `{"data": ..., "success": true, "message": "..."}`
- Error responses: `{"error": "CODE", "message": "...", "details": {...}}`

### Authentication
- JWT-based authentication with `get_current_user` dependency
- Role-based access with `get_current_superuser`
- Password hashing with bcrypt

### Database
- SQLAlchemy 2.0 with async support
- Use `get_db()` dependency for database sessions
- Models inherit from `BaseModel` with UUID primary keys

### Pagination
- Use `get_paginated_results()` utility for consistent pagination
- Supports search, sort, and filter parameters
- Standardized response format with metadata

### API Structure
- Routes organized by version (`/api/v1/`)
- Separated routers for different features (auth, posts, etc.)
- Automatic OpenAPI documentation generation

## Configuration

### Environment Variables
- Copy `.env.example` to `.env` and configure:
  - Database URL: `DATABASE_URL`
  - Redis URL: `REDIS_URL`
  - JWT secret: `SECRET_KEY`
  - Environment: `ENVIRONMENT`

### Key Dependencies
- **Package Management**: uv (modern Python package manager)
- **Web Framework**: FastAPI
- **Database**: SQLAlchemy 2.0 + PostgreSQL
- **Cache**: Redis
- **Authentication**: JWT + bcrypt
- **Testing**: pytest + pytest-asyncio
- **Code Quality**: Ruff + MyPy
- **Documentation**: OpenAPI/Swagger + ReDoc

## Docker Development

```bash
# Start all services (database, redis, app)
./dev.sh docker-dev

# Production deployment
./dev.sh docker-prod

# Individual services
docker-compose up postgres redis    # Database and Redis only
docker-compose up dev               # Development app with hot reload
```

## Testing

```bash
# Run all tests
./dev.sh test

# Run specific test file
uv run pytest tests/test_auth.py -v

# Run with coverage
uv run pytest --cov=app --cov-report=html
```

## Code Style

- **Formatting**: Ruff (configured in pyproject.toml)
- **Type Hints**: 100% type annotation coverage
- **Import Sorting**: Ruff's isort-compatible sorting
- **Line Length**: 88 characters
- **Pre-commit**: Git hooks configured for code quality

## Database Migrations

The project uses SQLAlchemy without Alembic for simplicity. Create tables manually:

```python
from app.database.session import create_tables
await create_tables()
```

## Adding New Features

1. **API Endpoints**: Create new router in `app/api/v1/`
2. **Models**: Add SQLAlchemy model in `app/models/models.py`
3. **Schemas**: Add Pydantic schema in `app/models/schemas.py`
4. **Authentication**: Use existing auth dependencies
5. **Pagination**: Use `get_paginated_results()` utility
6. **Response**: Apply `@handle_response()` decorator

## Common Tasks

### Create new API endpoint
```python
from app.core.decorators import handle_response
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/endpoint")
@handle_response("Operation successful")
async def create_item(data: ItemSchema):
    return {"data": await create_item(data)}
```

### Add database model
```python
from app.models.models import BaseModel
from sqlalchemy import Column, String

class NewModel(BaseModel):
    name = Column(String(100), nullable=False)
```

### Add authentication to endpoint
```python
from app.core.auth import get_current_active_user
from app.models.models import User

@router.get("/protected")
@handle_response()
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"data": current_user}
```
