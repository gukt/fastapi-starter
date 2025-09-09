# FastAPI 项目结构最佳实践

## 概述

本文档详细介绍了 FastAPI 项目的最佳实践结构，结合了领域驱动设计（DDD）的理念和 FastAPI 的特性，提供了一个既清晰又实用的项目架构。

## 设计原则

### 1. 领域驱动设计（DDD）
- **业务领域为中心**：以业务领域（如 auth、posts）作为组织单位
- **高内聚低耦合**：每个领域模块内部高内聚，模块之间低耦合
- **清晰边界**：明确各层职责，避免混乱的依赖关系

### 2. 简化优于复杂
- **避免过度工程化**：不要为小项目创建复杂的目录结构
- **实用主义**：选择对开发效率最有利的结构
- **渐进式演进**：结构应该能够随着项目成长而演进

### 3. FastAPI 最佳实践
- **依赖注入**：充分利用 FastAPI 的依赖注入系统
- **类型安全**：使用 Pydantic 进行数据验证和类型检查
- **异步优先**：采用异步编程模式提高性能

## 推荐的项目结构

```
app/
├── domain1/              # 业务领域 1
│   ├── models.py         # 数据模型 (SQLAlchemy)
│   ├── schemas.py        # 数据模式 (Pydantic)
│   ├── service.py        # 业务逻辑
│   ├── router.py         # API 路由
│   ├── dependencies.py   # 依赖注入
│   ├── constants.py      # 常量定义
│   └── exceptions.py     # 自定义异常
├── domain2/              # 业务领域 2
│   ├── models.py
│   ├── schemas.py
│   ├── service.py
│   ├── router.py
│   ├── dependencies.py
│   ├── constants.py
│   └── exceptions.py
├── core/                 # 核心基础设施
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库连接
│   ├── auth.py           # 认证服务
│   ├── logging.py        # 日志配置
│   └── decorators.py     # 通用装饰器
├── utils/                # 工具模块
│   ├── pagination.py     # 分页工具
│   ├── security.py       # 安全工具
│   └── validators.py     # 验证工具
└── main.py               # 应用入口
```

## 各层职责说明

### 1. 模型层 (models.py)
```python
# app/auth/models.py
from sqlalchemy import Column, String, Boolean
from app.models.models import BaseModel

class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
```

**职责**：
- 定义数据库表结构
- 建立模型关系
- 提供数据持久化接口

### 2. 模式层 (schemas.py)
```python
# app/auth/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    """用户基础模式"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """创建用户模式"""
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    """用户响应模式"""
    id: UUID
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
```

**职责**：
- 定义 API 输入输出数据结构
- 数据验证和序列化
- 提供 API 文档

### 3. 服务层 (service.py)
```python
# app/auth/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models import User
from app.auth.schemas import UserCreate

class AuthService:
    """认证服务"""
    
    @staticmethod
    async def create_user(
        db: AsyncSession, 
        user_data: UserCreate
    ) -> User:
        """创建用户"""
        # 业务逻辑
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
```

**职责**：
- 实现业务逻辑
- 协调多个模型操作
- 处理业务规则和验证

### 4. 路由层 (router.py)
```python
# app/auth/router.py
from fastapi import APIRouter, Depends
from app.auth.service import AuthService
from app.auth.schemas import UserCreate, UserResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register", response_model=dict)
@handle_response("用户创建成功")
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    user = await AuthService.create_user(db, user_data)
    return UserResponse.model_validate(user)
```

**职责**：
- 定义 API 端点
- 处理 HTTP 请求/响应
- 参数验证和错误处理

### 5. 依赖层 (dependencies.py)
```python
# app/auth/dependencies.py
from fastapi import Depends, HTTPException
from app.auth.models import User

async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    """获取当前用户"""
    user = authenticate_user(token)
    if not user:
        raise HTTPException(status_code=401)
    return user

class PermissionChecker:
    """权限检查器"""
    
    def __init__(self, required_permissions: list):
        self.required_permissions = required_permissions
    
    def __call__(self, current_user: User = Depends(get_current_user)):
        if not has_permissions(current_user, self.required_permissions):
            raise HTTPException(status_code=403)
        return current_user
```

**职责**：
- 提供可重用的依赖项
- 实现认证和授权逻辑
- 参数预处理和验证

### 6. 常量层 (constants.py)
```python
# app/auth/constants.py
from enum import Enum

class ErrorCode(str, Enum):
    """错误代码"""
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"

class AuthConstants:
    """认证常量"""
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    PASSWORD_MIN_LENGTH = 8
```

**职责**：
- 定义错误代码
- 配置常量值
- 枚举类型定义

### 7. 异常层 (exceptions.py)
```python
# app/auth/exceptions.py
from fastapi import HTTPException, status
from app.auth.constants import ErrorCode

class AuthException(HTTPException):
    """认证异常基类"""
    
    def __init__(self, error_code: ErrorCode, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": error_code.value,
                "message": message
            }
        )

class AuthenticationError(AuthException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(
            ErrorCode.AUTHENTICATION_ERROR,
            message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
```

**职责**：
- 定义业务异常
- 统一错误处理
- 提供有意义的错误信息

## 何时使用复杂结构

### 需要复杂结构的情况
- **大型企业项目**：多个团队协作开发
- **微服务架构**：需要清晰的模块边界
- **复杂业务逻辑**：需要分层架构来管理复杂性
- **长期维护项目**：需要良好的可扩展性

### 适合简化结构的情况
- **中小型项目**：单个团队开发
- **原型开发**：快速迭代和验证
- **创业公司**：需要快速推向市场
- **学习项目**：重点在功能而非架构

## 实施建议

### 1. 渐进式演进
```python
# 阶段 1：简单结构
app/
├── models.py
├── schemas.py
├── routes.py
└── main.py

# 阶段 2：按功能分离
app/
├── auth/
│   ├── models.py
│   ├── schemas.py
│   └── routes.py
├── posts/
│   ├── models.py
│   ├── schemas.py
│   └── routes.py
└── main.py

# 阶段 3：完整领域结构
app/
├── auth/
│   ├── models.py
│   ├── schemas.py
│   ├── service.py
│   ├── router.py
│   ├── dependencies.py
│   ├── constants.py
│   └── exceptions.py
└── main.py
```

### 2. 代码组织原则
- **单一职责**：每个文件只负责一个明确的职责
- **依赖方向**：高层模块不依赖低层模块，依赖抽象而非具体实现
- **接口隔离**：客户端不应该依赖它不需要的接口

### 3. 命名约定
- **模块名**：使用小写，多个单词用下划线分隔
- **类名**：使用 PascalCase，如 UserService
- **函数名**：使用小写，多个单词用下划线分隔
- **常量名**：使用大写，多个单词用下划线分隔

## 常见陷阱和解决方案

### 1. 过度设计
**问题**：为小项目创建复杂的目录结构
**解决**：根据项目实际需求选择合适复杂度的结构

### 2. 循环依赖
**问题**：模块之间相互导入导致循环依赖
**解决**：
- 重新设计模块边界
- 使用依赖注入
- 在运行时动态导入

### 3. 配置混乱
**问题**：配置散布在多个文件中
**解决**：
- 使用统一的配置管理
- 环境变量和配置文件分离
- 配置验证和默认值

## 参考资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Netflix Dispatch 项目](https://github.com/Netflix/dispatch)
- [领域驱动设计](https://domainlanguage.com/ddd/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

## 总结

一个好的项目结构应该：
1. **清晰易懂**：新开发者能够快速理解
2. **易于维护**：修改和扩展不会引入太多风险
3. **高效开发**：不会因为结构复杂而降低开发效率
4. **可扩展**：能够随着项目成长而演进

最重要的是，结构应该服务于项目，而不是让项目服务于结构。