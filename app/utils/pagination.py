from typing import Any, Dict, Optional, TypeVar, Generic, List
from fastapi import Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, Column
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
from math import ceil

from app.core.schemas import PaginationParams, PaginationMeta, FilterParams, SortParams
from app.core.logging import api_logger

T = TypeVar('T', bound=DeclarativeBase)


class Paginator(Generic[T]):
    """分页器"""
    
    def __init__(
        self,
        session: AsyncSession,
        model: type[T],
        page: int = 1,
        size: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ):
        self.session = session
        self.model = model
        self.page = page
        self.size = size
        self.filters = filters or {}
        self.sort_by = sort_by
        self.sort_order = sort_order.lower()
        
        # 验证分页参数
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Page must be greater than 0"
            )
        
        if size < 1 or size > 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Size must be between 1 and 100"
            )
    
    async def get_total_count(self) -> int:
        """获取总记录数"""
        query = select(func.count(self.model.id))
        
        # 应用过滤器
        if self.filters:
            conditions = []
            for field, value in self.filters.items():
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    if isinstance(value, str) and '%' in value:
                        conditions.append(column.ilike(value))
                    else:
                        conditions.append(column == value)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        result = await self.session.execute(query)
        return result.scalar()
    
    async def get_items(self) -> List[T]:
        """获取分页数据"""
        query = select(self.model)
        
        # 应用过滤器
        if self.filters:
            conditions = []
            for field, value in self.filters.items():
                if hasattr(self.model, field):
                    column = getattr(self.model, field)
                    if isinstance(value, str) and '%' in value:
                        conditions.append(column.ilike(value))
                    else:
                        conditions.append(column == value)
            
            if conditions:
                query = query.where(and_(*conditions))
        
        # 应用排序
        if self.sort_by and hasattr(self.model, self.sort_by):
            column = getattr(self.model, self.sort_by)
            if self.sort_order == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        else:
            # 默认按创建时间排序
            if hasattr(self.model, 'created_at'):
                query = query.order_by(self.model.created_at.desc())
        
        # 应用分页
        offset = (self.page - 1) * self.size
        query = query.offset(offset).limit(self.size)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def paginate(self) -> Dict[str, Any]:
        """执行分页查询"""
        total = await self.get_total_count()
        items = await self.get_items()
        
        # 计算分页元数据
        pages = ceil(total / self.size) if total > 0 else 0
        has_next = self.page < pages
        has_prev = self.page > 1
        
        meta = PaginationMeta(
            page=self.page,
            size=self.size,
            total=total,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        return {
            "items": items,
            "meta": meta
        }


class FilterBuilder:
    """过滤器构建器"""
    
    @staticmethod
    def build_search_filters(model: type[T], search_term: str, search_fields: List[str]) -> List[Any]:
        """构建搜索过滤器"""
        if not search_term or not search_fields:
            return []
        
        conditions = []
        for field in search_fields:
            if hasattr(model, field):
                column = getattr(model, field)
                conditions.append(column.ilike(f"%{search_term}%"))
        
        return [or_(*conditions)] if conditions else []
    
    @staticmethod
    def build_range_filters(model: type[T], field: str, min_val: Any, max_val: Any) -> List[Any]:
        """构建范围过滤器"""
        if not hasattr(model, field):
            return []
        
        column = getattr(model, field)
        conditions = []
        
        if min_val is not None:
            conditions.append(column >= min_val)
        
        if max_val is not None:
            conditions.append(column <= max_val)
        
        return conditions
    
    @staticmethod
    def build_exact_filters(model: type[T], filters: Dict[str, Any]) -> List[Any]:
        """构建精确匹配过滤器"""
        conditions = []
        
        for field, value in filters.items():
            if hasattr(model, field) and value is not None:
                column = getattr(model, field)
                conditions.append(column == value)
        
        return conditions


class SortBuilder:
    """排序构建器"""
    
    @staticmethod
    def build_sort_clause(model: type[T], sort_by: str, sort_order: str = "asc"):
        """构建排序子句"""
        if not hasattr(model, sort_by):
            # 默认按ID排序
            sort_by = "id"
        
        column = getattr(model, sort_by)
        
        if sort_order.lower() == "desc":
            return column.desc()
        else:
            return column.asc()


class QueryParams(BaseModel):
    """查询参数"""
    page: int = Query(1, ge=1, description="页码")
    size: int = Query(10, ge=1, le=100, description="每页大小")
    search: Optional[str] = Query(None, description="搜索关键词")
    sort_by: Optional[str] = Query(None, description="排序字段")
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="排序方向")
    
    class Config:
        extra = "allow"


async def get_paginated_results(
    session: AsyncSession,
    model: type[T],
    page: int = 1,
    size: int = 10,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
    search_term: Optional[str] = None,
    search_fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """获取分页结果"""
    
    # 构建过滤器
    filter_conditions = {}
    
    # 添加精确匹配过滤器
    if filters:
        filter_conditions.update(filters)
    
    # 添加搜索过滤器
    if search_term and search_fields:
        search_conditions = FilterBuilder.build_search_filters(model, search_term, search_fields)
        if search_conditions:
            # 这里可以更复杂地处理搜索条件
            pass
    
    paginator = Paginator(
        session=session,
        model=model,
        page=page,
        size=size,
        filters=filter_conditions,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return await paginator.paginate()