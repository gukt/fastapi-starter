# FastAPI Starter

一个现代化的 FastAPI 脚手架项目，用于快速启动 API 项目开发。

## 特性

- 🚀 **现代化技术栈**: FastAPI + SQLAlchemy + Redis + JWT
- 🔐 **完整的认证系统**: JWT 认证、用户管理、权限控制
- 📊 **统一响应格式**: 自动包装的成功/失败响应
- 🔍 **分页搜索过滤**: 完整的分页、排序、过滤功能
- 🎨 **优雅的日志系统**: 基于 Loguru 的彩色日志
- 🐳 **Docker 支持**: 开发和生产环境的 Docker 配置
- 🧪 **完整的测试**: 单元测试和集成测试
- 🔧 **开发工具**: 代码格式化、类型检查、预提交钩子
- 📚 **自动文档**: Swagger UI 和 ReDoc

## 技术栈

- **Web 框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy 2.0
- **缓存**: Redis
- **认证**: JWT + OAuth2
- **包管理**: uv
- **测试**: Pytest
- **工具**: Ruff + MyPy + Pre-commit
- **容器化**: Docker + Docker Compose

## 快速开始

### 前置要求

- Python 3.11+
- PostgreSQL
- Redis
- uv (Python 包管理器)

### 安装

1. **克隆项目**

```bash
git clone <repository-url>
cd fastapi-starter
```

2. **安装 uv**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **设置环境**

```bash
./dev.sh setup
```

4. **启动服务**

```bash
# 启动数据库和 Redis
docker-compose up -d postgres redis

# 启动开发服务器
./dev.sh dev
```

### 使用 Docker

```bash
# 开发环境
./dev.sh docker-dev

# 生产环境
./dev.sh docker-prod
```

## 项目结构

```
fastapi-starter/
├── app/
│   ├── api/              # API 路由
│   │   └── v1/           # API v1
│   ├── core/             # 核心模块
│   │   ├── auth.py       # 认证服务
│   │   ├── config.py     # 配置管理
│   │   ├── decorators.py # 响应装饰器
│   │   ├── logging.py    # 日志配置
│   │   └── redis.py      # Redis 缓存
│   ├── database/         # 数据库相关
│   │   └── session.py    # 数据库会话
│   ├── models/           # 数据模型
│   │   ├── models.py     # SQLAlchemy 模型
│   │   └── schemas.py    # Pydantic 模式
│   ├── utils/            # 工具模块
│   │   └── pagination.py # 分页工具
│   └── main.py           # 应用入口
├── tests/                # 测试文件
├── docs/                 # 文档
├── logs/                 # 日志文件
├── .env.example         # 环境变量模板
├── docker-compose.yml    # Docker Compose 配置
├── pyproject.toml       # 项目配置
└── dev.sh              # 开发脚本
```

## API 文档

启动服务器后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### 主要 API 端点

#### 认证接口

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息
- `PUT /api/v1/auth/me` - 更新用户信息
- `GET /api/v1/auth/users` - 获取用户列表
- `GET /api/v1/auth/users/{user_id}` - 获取用户详情

#### 文章接口

- `POST /api/v1/posts/` - 创建文章
- `GET /api/v1/posts/` - 获取文章列表
- `GET /api/v1/posts/{post_id}` - 获取文章详情
- `PUT /api/v1/posts/{post_id}` - 更新文章
- `DELETE /api/v1/posts/{post_id}` - 删除文章
- `GET /api/v1/posts/my/posts` - 获取我的文章

### 响应格式

#### 成功响应

```json
{
  "data": "响应数据",
  "success": true,
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 错误响应

```json
{
  "error": "ERROR_CODE",
  "message": "错误描述",
  "details": {
    "详细错误信息"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 分页参数

所有列表接口支持以下查询参数：

- `page` - 页码（默认：1）
- `size` - 每页大小（默认：10，最大：100）
- `search` - 搜索关键词
- `sort_by` - 排序字段
- `sort_order` - 排序方向（asc/desc）

## 开发指南

### 可用命令

```bash
# 设置开发环境
./dev.sh setup

# 安装依赖
./dev.sh install

# 启动开发服务器
./dev.sh dev

# 运行测试
./dev.sh test

# 代码格式化
./dev.sh format

# 类型检查
./dev.sh typecheck

# 创建超级用户
./dev.sh superuser

# 清理缓存
./dev.sh clean
```

### 环境变量

复制 `.env.example` 为 `.env` 并配置以下变量：

```env
# 应用配置
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# 数据库
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_starter

# Redis
REDIS_URL=redis://localhost:6379/0
```

### 数据库迁移

项目使用 SQLAlchemy，可以手动创建表：

```python
from app.database.session import create_tables
await create_tables()
```

### 添加新的 API 端点

1. 在 `app/api/v1/` 目录下创建新的路由文件
2. 在 `app/models/schemas.py` 中添加 Pydantic 模式
3. 在 `app/models/models.py` 中添加 SQLAlchemy 模型
4. 在 `app/api/v1/__init__.py` 中注册路由

### 自定义装饰器

使用 `@handle_response()` 装饰器自动包装响应：

```python
from app.core.decorators import handle_response

@router.post("/endpoint")
@handle_response("操作成功")
async def my_endpoint():
    return {"data": "返回数据"}
```

## 测试

运行测试：

```bash
./dev.sh test
```

运行特定测试：

```bash
uv run pytest tests/test_auth.py -v
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t fastapi-starter .

# 运行容器
docker run -p 8000:8000 fastapi-starter
```

### Docker Compose 部署

```bash
# 生产环境
./dev.sh docker-prod
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 更新日志

### v0.1.0

- 初始版本
- 完整的认证系统
- 分页搜索过滤
- 统一响应格式
- Docker 支持
- 完整的测试覆盖
