from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_active_user
from app.core.decorators import handle_exceptions, handle_response
from app.core.logging import api_logger
from app.database.session import get_db
from app.models.models import Post, User
from app.models.schemas import PostCreate, PostResponse, PostUpdate
from app.utils.pagination import QueryParams, get_paginated_results

router = APIRouter(prefix="/posts", tags=["文章"])


@router.post("/", response_model=dict, summary="创建文章")
@handle_response("文章创建成功")
@handle_exceptions()
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """创建文章"""
    # 检查slug是否已存在
    result = await db.execute(select(Post).where(Post.slug == post_data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug already exists"
        )

    # 创建文章
    db_post = Post(
        title=post_data.title,
        content=post_data.content,
        slug=post_data.slug,
        summary=post_data.summary,
        is_published=post_data.is_published,
        author_id=current_user.id
    )

    if post_data.is_published:
        from datetime import datetime
        db_post.published_at = datetime.utcnow()

    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)

    api_logger.info(f"New post created: {post_data.title} by {current_user.username}")
    return PostResponse.model_validate(db_post)


@router.get("/", response_model=dict, summary="获取文章列表")
@handle_response()
@handle_exceptions()
async def get_posts(
    params: QueryParams = Depends(),
    search: str | None = Query(None, description="搜索标题或内容"),
    is_published: bool | None = Query(None, description="是否发布"),
    author_id: UUID | None = Query(None, description="作者ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取文章列表"""
    filters = {}

    if is_published is not None:
        filters["is_published"] = is_published

    if author_id:
        filters["author_id"] = author_id

    # 如果不是超级用户，只能看到已发布的文章或自己的文章
    if not current_user.is_superuser:
        result = await get_paginated_results(
            session=db,
            model=Post,
            page=params.page,
            size=params.size,
            sort_by=params.sort_by or "created_at",
            sort_order=params.sort_order,
            search_term=search,
            search_fields=["title", "content", "summary"]
        )

        # 过滤结果
        filtered_items = []
        for post in result["items"]:
            if post.is_published or post.author_id == current_user.id:
                filtered_items.append(post)

        result["items"] = filtered_items
        result["meta"]["total"] = len(filtered_items)

    else:
        result = await get_paginated_results(
            session=db,
            model=Post,
            page=params.page,
            size=params.size,
            sort_by=params.sort_by or "created_at",
            sort_order=params.sort_order,
            search_term=search,
            search_fields=["title", "content", "summary"]
        )

    return {
        "items": [PostResponse.model_validate(post) for post in result["items"]],
        "meta": result["meta"]
    }


@router.get("/{post_id}", response_model=dict, summary="获取文章详情")
@handle_response()
@handle_exceptions()
async def get_post(
    post_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取文章详情"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # 检查权限
    if not post.is_published and post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return PostResponse.model_validate(post)


@router.put("/{post_id}", response_model=dict, summary="更新文章")
@handle_response("文章更新成功")
@handle_exceptions()
async def update_post(
    post_id: UUID,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新文章"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # 检查权限
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # 检查slug是否已被其他文章使用
    if post_data.slug and post_data.slug != post.slug:
        slug_result = await db.execute(
            select(Post).where(
                Post.slug == post_data.slug,
                Post.id != post_id
            )
        )
        if slug_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slug already exists"
            )

    # 更新文章
    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    # 如果发布状态改变，更新发布时间
    if "is_published" in update_data:
        from datetime import datetime
        if post.is_published and not post.published_at:
            post.published_at = datetime.utcnow()
        elif not post.is_published:
            post.published_at = None

    await db.commit()
    await db.refresh(post)

    api_logger.info(f"Post updated: {post.title} by {current_user.username}")
    return PostResponse.model_validate(post)


@router.delete("/{post_id}", response_model=dict, summary="删除文章")
@handle_response("文章删除成功")
@handle_exceptions()
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """删除文章"""
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # 检查权限
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    await db.delete(post)
    await db.commit()

    api_logger.info(f"Post deleted: {post.title} by {current_user.username}")
    return {"message": "Post deleted successfully"}


@router.get("/my/posts", response_model=dict, summary="获取我的文章")
@handle_response()
@handle_exceptions()
async def get_my_posts(
    params: QueryParams = Depends(),
    search: str | None = Query(None, description="搜索标题或内容"),
    is_published: bool | None = Query(None, description="是否发布"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取我的文章"""
    filters = {"author_id": current_user.id}

    if is_published is not None:
        filters["is_published"] = is_published

    result = await get_paginated_results(
        session=db,
        model=Post,
        page=params.page,
        size=params.size,
        sort_by=params.sort_by or "created_at",
        sort_order=params.sort_order,
        search_term=search,
        search_fields=["title", "content", "summary"]
    )

    return {
        "items": [PostResponse.model_validate(post) for post in result["items"]],
        "meta": result["meta"]
    }
