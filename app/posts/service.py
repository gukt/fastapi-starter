"""Posts 模块的服务层"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.core.logging import api_logger
from app.posts.exceptions import (
    NotAuthorError,
    PostNotFoundError,
    SlugAlreadyExistsError,
)
from app.posts.models import Post
from app.posts.schemas import PostCreate, PostUpdate


class PostService:
    """文章服务"""

    @staticmethod
    async def create_post(
        db: AsyncSession,
        post_data: PostCreate,
        author: User
    ) -> Post:
        """创建文章"""
        # 检查 slug 是否已存在
        result = await db.execute(select(Post).where(Post.slug == post_data.slug))
        if result.scalar_one_or_none():
            raise SlugAlreadyExistsError("Slug already exists")

        # 创建文章
        db_post = Post(
            title=post_data.title,
            content=post_data.content,
            slug=post_data.slug,
            summary=post_data.summary,
            is_published=post_data.is_published,
            author_id=author.id
        )

        if post_data.is_published:
            db_post.published_at = datetime.utcnow()

        db.add(db_post)
        await db.commit()
        await db.refresh(db_post)

        api_logger.info(f"New post created: {post_data.title} by {author.username}")
        return db_post

    @staticmethod
    async def get_post_by_id(db: AsyncSession, post_id: UUID) -> Post | None:
        """根据 ID 获取文章"""
        result = await db.execute(select(Post).where(Post.id == post_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_post_by_slug(db: AsyncSession, slug: str) -> Post | None:
        """根据 slug 获取文章"""
        result = await db.execute(select(Post).where(Post.slug == slug))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_posts(
        db: AsyncSession,
        page: int = 1,
        size: int = 10,
        search: str | None = None,
        is_published: bool | None = None,
        author_id: UUID | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> dict:
        """获取文章列表"""
        from app.utils.pagination import get_paginated_results

        filters = {}
        if is_published is not None:
            filters["is_published"] = is_published
        if author_id:
            filters["author_id"] = author_id

        result = await get_paginated_results(
            session=db,
            model=Post,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order,
            search_term=search,
            search_fields=["title", "content", "summary"],
            filters=filters
        )

        return result

    @staticmethod
    async def update_post(
        db: AsyncSession,
        post_id: UUID,
        post_data: PostUpdate,
        current_user: User
    ) -> Post:
        """更新文章"""
        post = await PostService.get_post_by_id(db, post_id)
        if not post:
            raise PostNotFoundError("Post not found")

        # 检查权限
        if post.author_id != current_user.id and not current_user.is_superuser:
            raise NotAuthorError("You are not the author of this post")

        # 检查 slug 是否已被其他文章使用
        if post_data.slug and post_data.slug != post.slug:
            slug_result = await db.execute(
                select(Post).where(
                    Post.slug == post_data.slug,
                    Post.id != post_id
                )
            )
            if slug_result.scalar_one_or_none():
                raise SlugAlreadyExistsError("Slug already exists")

        # 更新文章
        update_data = post_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)

        # 如果发布状态改变，更新发布时间
        if "is_published" in update_data:
            if post.is_published and not post.published_at:
                post.published_at = datetime.utcnow()
            elif not post.is_published:
                post.published_at = None

        await db.commit()
        await db.refresh(post)

        api_logger.info(f"Post updated: {post.title} by {current_user.username}")
        return post

    @staticmethod
    async def delete_post(
        db: AsyncSession,
        post_id: UUID,
        current_user: User
    ) -> bool:
        """删除文章"""
        post = await PostService.get_post_by_id(db, post_id)
        if not post:
            raise PostNotFoundError("Post not found")

        # 检查权限
        if post.author_id != current_user.id and not current_user.is_superuser:
            raise NotAuthorError("You are not the author of this post")

        await db.delete(post)
        await db.commit()

        api_logger.info(f"Post deleted: {post.title} by {current_user.username}")
        return True

    @staticmethod
    async def check_post_access(
        post: Post,
        current_user: User
    ) -> bool:
        """检查文章访问权限"""
        # 如果文章已发布，任何人都可以访问
        if post.is_published:
            return True

        # 如果是作者或超级用户，可以访问未发布的文章
        if post.author_id == current_user.id or current_user.is_superuser:
            return True

        return False

    @staticmethod
    async def get_user_posts(
        db: AsyncSession,
        user_id: UUID,
        page: int = 1,
        size: int = 10,
        search: str | None = None,
        is_published: bool | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> dict:
        """获取用户的文章列表"""
        return await PostService.get_posts(
            db=db,
            page=page,
            size=size,
            search=search,
            is_published=is_published,
            author_id=user_id,
            sort_by=sort_by,
            sort_order=sort_order
        )
