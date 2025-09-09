"""Posts 模块的依赖项"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.auth.models import User
from app.database.session import get_db
from app.posts.models import Post


async def get_post_by_id(
    post_id,
    db: AsyncSession = Depends(get_db)
) -> Post:
    """根据 ID 获取文章"""
    from sqlalchemy import select

    from app.posts.exceptions import PostNotFoundError
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise PostNotFoundError("Post not found")

    return post


async def get_post_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
) -> Post:
    """根据 slug 获取文章"""
    from sqlalchemy import select

    from app.posts.exceptions import PostNotFoundError
    result = await db.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()

    if not post:
        raise PostNotFoundError("Post not found")

    return post


async def check_post_ownership(
    post: Post = Depends(get_post_by_id),
    current_user: User = Depends(get_current_active_user)
) -> Post:
    """检查文章所有权"""
    from app.posts.exceptions import NotAuthorError

    if post.author_id != current_user.id and not current_user.is_superuser:
        raise NotAuthorError("You are not the author of this post")

    return post


async def check_post_access(
    post: Post = Depends(get_post_by_id),
    current_user: User = Depends(get_current_active_user)
) -> Post:
    """检查文章访问权限"""
    from app.posts.exceptions import AccessDeniedError

    # 如果文章已发布，任何人都可以访问
    if post.is_published:
        return post

    # 如果是作者或超级用户，可以访问未发布的文章
    if post.author_id == current_user.id or current_user.is_superuser:
        return post

    raise AccessDeniedError("Access denied")


class PostPermissionChecker:
    """文章权限检查器"""

    def __init__(self, require_author: bool = False):
        self.require_author = require_author

    def __call__(self, post: Post = Depends(get_post_by_id), current_user: User = Depends(get_current_active_user)):
        from app.posts.exceptions import AccessDeniedError, NotAuthorError

        # 检查访问权限
        if not post.is_published and post.author_id != current_user.id and not current_user.is_superuser:
            raise AccessDeniedError("Access denied")

        # 检查作者权限
        if self.require_author and post.author_id != current_user.id and not current_user.is_superuser:
            raise NotAuthorError("You are not the author of this post")

        return post


# 常用权限检查依赖
require_post_access = PostPermissionChecker(require_author=False)
require_post_author = PostPermissionChecker(require_author=True)
