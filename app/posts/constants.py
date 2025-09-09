"""Posts 模块的常量定义"""

from enum import Enum


class ErrorCode(str, Enum):
    """Posts 模块错误代码"""

    # 文章相关错误
    POST_NOT_FOUND = "POST_NOT_FOUND"
    POST_ALREADY_EXISTS = "POST_ALREADY_EXISTS"
    SLUG_ALREADY_EXISTS = "SLUG_ALREADY_EXISTS"

    # 权限相关错误
    ACCESS_DENIED = "ACCESS_DENIED"
    NOT_AUTHOR = "NOT_AUTHOR"

    # 验证相关错误
    INVALID_TITLE = "INVALID_TITLE"
    INVALID_CONTENT = "INVALID_CONTENT"
    INVALID_SLUG = "INVALID_SLUG"

    # 状态相关错误
    POST_NOT_PUBLISHED = "POST_NOT_PUBLISHED"
    POST_ALREADY_PUBLISHED = "POST_ALREADY_PUBLISHED"


class PostConstants:
    """Posts 模块常量"""

    # 文章相关
    MIN_TITLE_LENGTH = 1
    MAX_TITLE_LENGTH = 200
    MIN_CONTENT_LENGTH = 1
    MAX_CONTENT_LENGTH = 10000
    MAX_SUMMARY_LENGTH = 500
    MAX_SLUG_LENGTH = 100

    # 分页相关
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100

    # 排序相关
    DEFAULT_SORT_BY = "created_at"
    ALLOWED_SORT_FIELDS = ["created_at", "updated_at", "published_at", "title", "views"]
