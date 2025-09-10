#!/bin/bash

# FastAPI 开发脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否安装了uv
check_uv() {
    if ! command -v uv &> /dev/null; then
        log_error "uv is not installed. Please install it first:"
        echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
}

# 检查是否安装了Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_warning "Docker is not installed. Some features may not work."
    fi
}

# 设置环境
setup_env() {
    log_info "Setting up environment..."
    
    if [ ! -f ".env" ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
        log_success ".env file created. Please edit it with your settings."
    fi
    
    # 创建必要的目录
    mkdir -p logs uploads
}

# 安装依赖
install_deps() {
    log_info "Installing dependencies..."
    uv sync
    log_success "Dependencies installed successfully."
}

# 开发模式启动
dev() {
    log_info "Starting development server..."
    
    # 检查端口 8000 是否被占用
    if netstat -tulpn 2>/dev/null | grep :8000 >/dev/null; then
        log_warning "Port 8000 is already in use, using port 8001 instead..."
        uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
    else
        uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    fi
}

# 生产模式启动
prod() {
    log_info "Starting production server..."
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
}

# 运行测试
test() {
    log_info "Running tests..."
    uv run pytest -v --cov=app --cov-report=html --cov-report=term
}

# 代码格式化
format() {
    log_info "Formatting code..."
    uv run ruff check --fix .
    uv run ruff format .
    log_success "Code formatted successfully."
}

# 类型检查
typecheck() {
    log_info "Running type checking..."
    uv run mypy app
    log_success "Type checking completed."
}

# 数据库迁移
migrate() {
    log_info "Running database migrations..."
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter alembic upgrade head
    log_success "Database migrations completed."
}

# 创建迁移文件
migration_create() {
    log_info "Creating new migration..."
    if [ -z "$2" ]; then
        log_error "Please provide a migration name"
        echo "Usage: $0 migration-create \"migration name\""
        exit 1
    fi
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter alembic revision --autogenerate -m "$2"
    log_success "Migration created successfully."
}

# 回滚迁移
migrate_down() {
    log_info "Rolling back database migrations..."
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter alembic downgrade -1
    log_success "Database rollback completed."
}

# 查看迁移历史
migrate_history() {
    log_info "Migration history:"
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter alembic history --verbose
}

# 查看当前迁移状态
migrate_current() {
    log_info "Current migration status:"
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter alembic current
}

# 创建超级用户
create_superuser() {
    log_info "Creating superuser..."
    uv run python -c "
from app.database.session import create_tables
from app.core.auth import AuthService
from app.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio

async def create_superuser():
    engine = create_async_engine('postgresql+asyncpg://user:password@localhost:5432/fastapi_starter')
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if superuser already exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.email == 'admin@example.com'))
        if result.scalar_one_or_none():
            print('Superuser already exists')
            return
        
        # Create superuser
        hashed_password = AuthService.get_password_hash('admin123')
        superuser = User(
            email='admin@example.com',
            username='admin',
            full_name='Administrator',
            hashed_password=hashed_password,
            is_superuser=True,
            is_verified=True
        )
        session.add(superuser)
        await session.commit()
        print('Superuser created successfully')

asyncio.run(create_superuser())
"
    log_success "Superuser created: admin@example.com / admin123"
}

# Docker开发环境
docker_dev() {
    log_info "Starting Docker development environment..."
    docker-compose up dev
}

# Docker生产环境
docker_prod() {
    log_info "Starting Docker production environment..."
    docker-compose up -d
}

# 停止Docker
docker_stop() {
    log_info "Stopping Docker containers..."
    docker-compose down
}

# 清理
clean() {
    log_info "Cleaning up..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    rm -rf .pytest_cache .mypy_cache htmlcov logs/*.log
    log_success "Cleanup completed."
}

# 显示帮助
show_help() {
    echo "FastAPI Starter Development Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup               - Setup development environment"
    echo "  install             - Install dependencies"
    echo "  dev                 - Start development server"
    echo "  prod                - Start production server"
    echo "  test                - Run tests"
    echo "  format              - Format code"
    echo "  typecheck           - Run type checking"
    echo "  migrate             - Run database migrations"
    echo "  migration-create    - Create new migration (requires name)"
    echo "  migrate-down        - Rollback last migration"
    echo "  migrate-history     - Show migration history"
    echo "  migrate-current      - Show current migration status"
    echo "  superuser           - Create superuser"
    echo "  docker-dev          - Start Docker development environment"
    echo "  docker-prod         - Start Docker production environment"
    echo "  docker-stop         - Stop Docker containers"
    echo "  clean               - Clean up cache files"
    echo "  help                - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 migration-create \"add_user_table\""
    echo "  $0 migrate-down"
    echo "  $0 migrate-history"
    echo ""
}

# 主函数
main() {
    case "$1" in
        setup)
            check_uv
            setup_env
            install_deps
            log_success "Environment setup completed!"
            ;;
        install)
            check_uv
            install_deps
            ;;
        dev)
            check_uv
            dev
            ;;
        prod)
            check_uv
            prod
            ;;
        test)
            check_uv
            test
            ;;
        format)
            check_uv
            format
            ;;
        typecheck)
            check_uv
            typecheck
            ;;
        migrate)
            check_uv
            migrate
            ;;
        migration-create)
            check_uv
            migration_create "$@"
            ;;
        migrate-down)
            check_uv
            migrate_down
            ;;
        migrate-history)
            check_uv
            migrate_history
            ;;
        migrate-current)
            check_uv
            migrate_current
            ;;
        superuser)
            check_uv
            create_superuser
            ;;
        docker-dev)
            check_docker
            docker_dev
            ;;
        docker-prod)
            check_docker
            docker_prod
            ;;
        docker-stop)
            check_docker
            docker_stop
            ;;
        clean)
            clean
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"