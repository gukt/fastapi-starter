# 领域模块开发指南

## 概述

本指南提供了创建新领域模块的详细步骤和最佳实践。

## 创建新领域模块

### 步骤 1：创建目录结构

```bash
# 创建新的领域目录
mkdir -p app/products/

# 创建必要的文件
touch app/products/__init__.py
touch app/products/models.py
touch app/products/schemas.py
touch app/products/service.py
touch app/products/router.py
touch app/products/dependencies.py
touch app/products/constants.py
touch app/products/exceptions.py
```

### 步骤 2：定义数据模型 (models.py)

```python
# app/products/models.py
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.models import BaseModel

class Product(BaseModel):
    """产品模型"""
    __tablename__ = "products"
    
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    
    # 关系
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

class Category(BaseModel):
    """分类模型"""
    __tablename__ = "categories"
    
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # 关系
    products = relationship("Product", back_populates="category")
```

### 步骤 3：定义数据模式 (schemas.py)

```python
# app/products/schemas.py
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional, List

class ProductBase(BaseModel):
    """产品基础模式"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Decimal = Field(..., gt=0)
    stock: int = Field(0, ge=0)
    is_active: bool = True
    category_id: UUID

class ProductCreate(ProductBase):
    """创建产品模式"""
    pass

class ProductUpdate(BaseModel):
    """更新产品模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[Decimal] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    category_id: Optional[UUID] = None

class ProductResponse(ProductBase):
    """产品响应模式"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    """分类基础模式"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class CategoryCreate(CategoryBase):
    """创建分类模式"""
    pass

class CategoryResponse(CategoryBase):
    """分类响应模式"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    products: List[ProductResponse] = []
    
    class Config:
        from_attributes = True
```

### 步骤 4：实现业务逻辑 (service.py)

```python
# app/products/service.py
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.products.models import Product, Category
from app.products.schemas import ProductCreate, ProductUpdate, CategoryCreate
from app.core.logging import api_logger

class ProductService:
    """产品服务"""
    
    @staticmethod
    async def create_product(
        db: AsyncSession,
        product_data: ProductCreate
    ) -> Product:
        """创建产品"""
        # 验证分类是否存在
        category_result = await db.execute(
            select(Category).where(Category.id == product_data.category_id)
        )
        category = category_result.scalar_one_or_none()
        if not category:
            from app.products.exceptions import CategoryNotFoundError
            raise CategoryNotFoundError("Category not found")
        
        # 创建产品
        db_product = Product(**product_data.model_dump())
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        
        api_logger.info(f"Product created: {product_data.name}")
        return db_product
    
    @staticmethod
    async def get_product_by_id(
        db: AsyncSession,
        product_id: UUID
    ) -> Optional[Product]:
        """根据 ID 获取产品"""
        result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_products(
        db: AsyncSession,
        page: int = 1,
        size: int = 10,
        category_id: Optional[UUID] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> dict:
        """获取产品列表"""
        from app.utils.pagination import get_paginated_results
        
        filters = {}
        if category_id:
            filters["category_id"] = category_id
        if is_active is not None:
            filters["is_active"] = is_active
        
        result = await get_paginated_results(
            session=db,
            model=Product,
            page=page,
            size=size,
            search_term=search,
            search_fields=["name", "description"],
            filters=filters
        )
        
        # 应用价格过滤
        items = result["items"]
        if min_price is not None:
            items = [p for p in items if p.price >= min_price]
        if max_price is not None:
            items = [p for p in items if p.price <= max_price]
        
        result["items"] = items
        result["meta"]["total"] = len(items)
        
        return result
    
    @staticmethod
    async def update_product(
        db: AsyncSession,
        product_id: UUID,
        product_data: ProductUpdate
    ) -> Product:
        """更新产品"""
        product = await ProductService.get_product_by_id(db, product_id)
        if not product:
            from app.products.exceptions import ProductNotFoundError
            raise ProductNotFoundError("Product not found")
        
        # 如果更新分类，验证分类是否存在
        if product_data.category_id:
            category_result = await db.execute(
                select(Category).where(Category.id == product_data.category_id)
            )
            category = category_result.scalar_one_or_none()
            if not category:
                from app.products.exceptions import CategoryNotFoundError
                raise CategoryNotFoundError("Category not found")
        
        # 更新产品
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        await db.commit()
        await db.refresh(product)
        
        api_logger.info(f"Product updated: {product.name}")
        return product
    
    @staticmethod
    async def delete_product(
        db: AsyncSession,
        product_id: UUID
    ) -> bool:
        """删除产品"""
        product = await ProductService.get_product_by_id(db, product_id)
        if not product:
            from app.products.exceptions import ProductNotFoundError
            raise ProductNotFoundError("Product not found")
        
        await db.delete(product)
        await db.commit()
        
        api_logger.info(f"Product deleted: {product.name}")
        return True

class CategoryService:
    """分类服务"""
    
    @staticmethod
    async def create_category(
        db: AsyncSession,
        category_data: CategoryCreate
    ) -> Category:
        """创建分类"""
        # 检查分类名称是否已存在
        result = await db.execute(
            select(Category).where(Category.name == category_data.name)
        )
        if result.scalar_one_or_none():
            from app.products.exceptions import CategoryAlreadyExistsError
            raise CategoryAlreadyExistsError("Category already exists")
        
        # 创建分类
        db_category = Category(**category_data.model_dump())
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        
        api_logger.info(f"Category created: {category_data.name}")
        return db_category
    
    @staticmethod
    async def get_categories(
        db: AsyncSession,
        page: int = 1,
        size: int = 10
    ) -> dict:
        """获取分类列表"""
        from app.utils.pagination import get_paginated_results
        
        return await get_paginated_results(
            session=db,
            model=Category,
            page=page,
            size=size
        )
```

### 步骤 5：定义 API 路由 (router.py)

```python
# app/products/router.py
from typing import Optional
from uuid import UUID
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.core.decorators import handle_response, handle_exceptions
from app.database.session import get_db
from app.auth.models import User
from app.products.service import ProductService, CategoryService
from app.products.schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    CategoryCreate, CategoryResponse
)
from app.utils.pagination import QueryParams

router = APIRouter(prefix="/products", tags=["产品"])

# 产品相关路由
@router.post("/", response_model=dict)
@handle_response("产品创建成功")
@handle_exceptions()
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建产品"""
    product = await ProductService.create_product(db, product_data)
    return ProductResponse.model_validate(product)

@router.get("/", response_model=dict)
@handle_response()
@handle_exceptions()
async def get_products(
    params: QueryParams = Depends(),
    category_id: Optional[UUID] = Query(None, description="分类 ID"),
    min_price: Optional[Decimal] = Query(None, description="最低价格"),
    max_price: Optional[Decimal] = Query(None, description="最高价格"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取产品列表"""
    result = await ProductService.get_products(
        db=db,
        page=params.page,
        size=params.size,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        is_active=is_active,
        search=search
    )
    
    return {
        "items": [ProductResponse.model_validate(p) for p in result["items"]],
        "meta": result["meta"]
    }

@router.get("/{product_id}", response_model=dict)
@handle_response()
@handle_exceptions()
async def get_product(
    product_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取产品详情"""
    product = await ProductService.get_product_by_id(db, product_id)
    if not product:
        from app.products.exceptions import ProductNotFoundError
        raise ProductNotFoundError("Product not found")
    
    return ProductResponse.model_validate(product)

@router.put("/{product_id}", response_model=dict)
@handle_response("产品更新成功")
@handle_exceptions()
async def update_product(
    product_id: UUID,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新产品"""
    product = await ProductService.update_product(db, product_id, product_data)
    return ProductResponse.model_validate(product)

@router.delete("/{product_id}", response_model=dict)
@handle_response("产品删除成功")
@handle_exceptions()
async def delete_product(
    product_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除产品"""
    await ProductService.delete_product(db, product_id)
    return {"message": "Product deleted successfully"}

# 分类相关路由
@router.post("/categories/", response_model=dict)
@handle_response("分类创建成功")
@handle_exceptions()
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建分类"""
    category = await CategoryService.create_category(db, category_data)
    return CategoryResponse.model_validate(category)

@router.get("/categories/", response_model=dict)
@handle_response()
@handle_exceptions()
async def get_categories(
    params: QueryParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取分类列表"""
    result = await CategoryService.get_categories(
        db=db,
        page=params.page,
        size=params.size
    )
    
    return {
        "items": [CategoryResponse.model_validate(c) for c in result["items"]],
        "meta": result["meta"]
    }
```

### 步骤 6：定义依赖项 (dependencies.py)

```python
# app/products/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.products.models import Product, Category
from app.database.session import get_db

async def get_product_by_id(
    product_id,
    db: AsyncSession = Depends(get_db)
) -> Product:
    """根据 ID 获取产品"""
    from app.products.exceptions import ProductNotFoundError
    
    from sqlalchemy import select
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise ProductNotFoundError("Product not found")
    
    return product

async def get_category_by_id(
    category_id,
    db: AsyncSession = Depends(get_db)
) -> Category:
    """根据 ID 获取分类"""
    from app.products.exceptions import CategoryNotFoundError
    
    from sqlalchemy import select
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    
    if not category:
        raise CategoryNotFoundError("Category not found")
    
    return category

async def check_product_availability(
    product: Product = Depends(get_product_by_id)
) -> Product:
    """检查产品可用性"""
    if not product.is_active:
        from app.products.exceptions import ProductNotAvailableError
        raise ProductNotAvailableError("Product is not available")
    
    if product.stock <= 0:
        from app.products.exceptions import ProductOutOfStockError
        raise ProductOutOfStockError("Product is out of stock")
    
    return product
```

### 步骤 7：定义常量 (constants.py)

```python
# app/products/constants.py
from enum import Enum

class ErrorCode(str, Enum):
    """产品模块错误代码"""
    
    # 产品相关错误
    PRODUCT_NOT_FOUND = "PRODUCT_NOT_FOUND"
    PRODUCT_ALREADY_EXISTS = "PRODUCT_ALREADY_EXISTS"
    PRODUCT_NOT_AVAILABLE = "PRODUCT_NOT_AVAILABLE"
    PRODUCT_OUT_OF_STOCK = "PRODUCT_OUT_OF_STOCK"
    
    # 分类相关错误
    CATEGORY_NOT_FOUND = "CATEGORY_NOT_FOUND"
    CATEGORY_ALREADY_EXISTS = "CATEGORY_ALREADY_EXISTS"
    
    # 验证相关错误
    INVALID_PRICE = "INVALID_PRICE"
    INVALID_STOCK = "INVALID_STOCK"
    INVALID_PRODUCT_NAME = "INVALID_PRODUCT_NAME"

class ProductConstants:
    """产品模块常量"""
    
    # 产品相关
    MIN_PRODUCT_NAME_LENGTH = 1
    MAX_PRODUCT_NAME_LENGTH = 200
    MAX_PRODUCT_DESCRIPTION_LENGTH = 1000
    MIN_PRICE = 0.01
    MAX_PRICE = 999999.99
    MIN_STOCK = 0
    MAX_STOCK = 999999
    
    # 分类相关
    MIN_CATEGORY_NAME_LENGTH = 1
    MAX_CATEGORY_NAME_LENGTH = 100
    MAX_CATEGORY_DESCRIPTION_LENGTH = 500
    
    # 分页相关
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
```

### 步骤 8：定义异常 (exceptions.py)

```python
# app/products/exceptions.py
from fastapi import HTTPException, status
from typing import Optional, Dict, Any

from app.products.constants import ErrorCode

class ProductException(HTTPException):
    """产品模块异常基类"""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": error_code.value,
                "message": message,
                "details": details or {}
            }
        )

class ProductNotFoundError(ProductException):
    """产品未找到异常"""
    
    def __init__(self, message: str = "Product not found"):
        super().__init__(
            ErrorCode.PRODUCT_NOT_FOUND,
            message,
            status_code=status.HTTP_404_NOT_FOUND
        )

class ProductAlreadyExistsError(ProductException):
    """产品已存在异常"""
    
    def __init__(self, message: str = "Product already exists"):
        super().__init__(
            ErrorCode.PRODUCT_ALREADY_EXISTS,
            message,
            status_code=status.HTTP_409_CONFLICT
        )

class ProductNotAvailableError(ProductException):
    """产品不可用异常"""
    
    def __init__(self, message: str = "Product is not available"):
        super().__init__(
            ErrorCode.PRODUCT_NOT_AVAILABLE,
            message,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class ProductOutOfStockError(ProductException):
    """产品缺货异常"""
    
    def __init__(self, message: str = "Product is out of stock"):
        super().__init__(
            ErrorCode.PRODUCT_OUT_OF_STOCK,
            message,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class CategoryNotFoundError(ProductException):
    """分类未找到异常"""
    
    def __init__(self, message: str = "Category not found"):
        super().__init__(
            ErrorCode.CATEGORY_NOT_FOUND,
            message,
            status_code=status.HTTP_404_NOT_FOUND
        )

class CategoryAlreadyExistsError(ProductException):
    """分类已存在异常"""
    
    def __init__(self, message: str = "Category already exists"):
        super().__init__(
            ErrorCode.CATEGORY_ALREADY_EXISTS,
            message,
            status_code=status.HTTP_409_CONFLICT
        )
```

### 步骤 9：注册路由

```python
# app/api/v1/__init__.py
from fastapi import APIRouter
from app.auth.router import router as auth_router
from app.posts.router import router as posts_router
from app.products.router import router as products_router

api_router = APIRouter()

# 注册路由
api_router.include_router(auth_router)
api_router.include_router(posts_router)
api_router.include_router(products_router)
```

## 测试新模块

```python
# tests/test_products.py
import pytest
from httpx import AsyncClient
from app.products.schemas import ProductCreate

@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, auth_headers):
    """测试创建产品"""
    # 首先创建分类
    category_data = {"name": "测试分类", "description": "测试分类描述"}
    category_response = await client.post(
        "/api/v1/products/categories/",
        json=category_data,
        headers=auth_headers
    )
    assert category_response.status_code == 200
    
    category_id = category_response.json()["data"]["id"]
    
    # 创建产品
    product_data = {
        "name": "测试产品",
        "description": "测试产品描述",
        "price": 99.99,
        "stock": 100,
        "category_id": category_id
    }
    
    response = await client.post(
        "/api/v1/products/",
        json=product_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]
```

## 最佳实践

1. **遵循命名约定**：文件名使用小写，类名使用 PascalCase
2. **使用类型注解**：为所有函数和变量添加类型注解
3. **错误处理**：使用自定义异常类，提供有意义的错误信息
4. **日志记录**：在关键操作中添加适当的日志记录
5. **输入验证**：使用 Pydantic 进行严格的输入验证
6. **依赖注入**：充分利用 FastAPI 的依赖注入系统
7. **文档字符串**：为所有公共函数和类添加文档字符串
8. **单元测试**：为每个服务方法编写单元测试

## 常见问题

### Q: 如何处理跨模块的依赖？
A: 通过依赖注入和接口抽象来处理，避免直接依赖具体实现。

### Q: 如何处理复杂的业务逻辑？
A: 在服务层中实现复杂的业务逻辑，保持路由层的简洁。

### Q: 如何优化数据库查询？
A: 使用 SQLAlchemy 的异步查询，合理使用索引和连接查询。

### Q: 如何处理大规模数据？
A: 使用分页、缓存和异步处理来优化性能。