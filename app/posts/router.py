"""Posts 模块的路由层"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.core.decorators import handle_exceptions, handle_response
from app.database.session import get_db
from app.posts.exceptions import AccessDeniedError, PostNotFoundError
from app.posts.schemas import PostCreate, PostResponse, PostUpdate
from app.posts.service import PostService
from app.utils.pagination import QueryParams

router = APIRouter(prefix="/posts", tags=["文章"])


@router.post("/", response_model=dict, summary="创建文章")
@handle_response("文章创建成功")
@handle_exceptions()
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """创建文章"""
    post = await PostService.create_post(db, post_data, current_user)
    return PostResponse.model_validate(post)


@router.get("/", response_model=dict, summary="获取文章列表1")
@handle_response()
@handle_exceptions()
async def get_posts(
    params: QueryParams = Depends(),
    search: str | None = Query(None, description="搜索标题或内容"),
    is_published: bool | None = Query(None, description="是否发布"),
    author_id: UUID | None = Query(None, description="作者 ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取文章列表"""
    result = await PostService.get_posts(
        db=db,
        page=params.page,
        size=params.size,
        search=search,
        is_published=is_published,
        author_id=author_id,
        sort_by=params.sort_by or "created_at",
        sort_order=params.sort_order,
    )

    # 如果不是超级用户，过滤掉未发布的非自己文章
    if not current_user.is_superuser:
        filtered_items = []
        for post in result["items"]:
            if await PostService.check_post_access(post, current_user):
                filtered_items.append(post)

        result["items"] = filtered_items
        result["meta"]["total"] = len(filtered_items)

    return {
        "items": [PostResponse.model_validate(post) for post in result["items"]],
        "meta": result["meta"],
    }


@router.get("/{post_id}", response_model=dict, summary="获取文章详情")
@handle_response()
@handle_exceptions()
async def get_post(
    post_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取文章详情"""
    post = await PostService.get_post_by_id(db, post_id)
    if not post:
        raise PostNotFoundError("Post not found")

    # 检查访问权限
    if not await PostService.check_post_access(post, current_user):
        raise AccessDeniedError("Access denied")

    return PostResponse.model_validate(post)


@router.put("/{post_id}", response_model=dict, summary="更新文章")
@handle_response("文章更新成功")
@handle_exceptions()
async def update_post(
    post_id: UUID,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """更新文章"""
    post = await PostService.update_post(db, post_id, post_data, current_user)
    return PostResponse.model_validate(post)


@router.delete("/{post_id}", response_model=dict, summary="删除文章")
@handle_response("文章删除成功")
@handle_exceptions()
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """删除文章"""
    await PostService.delete_post(db, post_id, current_user)
    return {"message": "Post deleted successfully"}


@router.get("/my/posts", response_model=dict, summary="获取我的文章")
@handle_response()
@handle_exceptions()
async def get_my_posts(
    params: QueryParams = Depends(),
    search: str | None = Query(None, description="搜索标题或内容"),
    is_published: bool | None = Query(None, description="是否发布"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取我的文章"""
    result = await PostService.get_user_posts(
        db=db,
        user_id=current_user.id,
        page=params.page,
        size=params.size,
        search=search,
        is_published=is_published,
        sort_by=params.sort_by or "created_at",
        sort_order=params.sort_order,
    )

    return {
        "items": [PostResponse.model_validate(post) for post in result["items"]],
        "meta": result["meta"],
    }
