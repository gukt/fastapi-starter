"""自定义异常模块"""

from typing import Any

from fastapi import HTTPException


class BaseAppError(HTTPException):
    """应用程序异常基类

    继承自 FastAPI 的 HTTPException, 同时提供更多字段和功能：
    - error_code: 业务错误码（字符串）
    - details: 错误详情（可选）
    """

    status_code: int = 500
    error_code: str = "server_error"
    message: str = "Server Error."
    details: dict[str, Any] | None = None

    def __init__(
        self,
        status_code: int | None = None,
        error_code: str | None = None,
        message: str | None = None,
        details: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ):
        self.status_code = status_code or self.status_code
        self.error_code = error_code or self.error_code
        self.message = message or self.message
        self.details = details

        # 调用父类初始化
        super().__init__(
            status_code=self.status_code,
            detail=self.message,  # 注意：父类 detail 参数就是当前类的 message
            headers=headers,
        )

    def to_dict(self) -> dict[str, Any]:
        """将异常转换为统一的错误响应字典"""
        error = {
            "code": self.error_code,
            "message": self.message,
        }
        if self.details:
            error["details"] = self.details
        return error


class ResourceNotFoundError(BaseAppError):
    """资源未找到异常"""

    status_code = 404
    error_code = "resource_not_found"
    message = "请求的资源不存在"


class ValidationError(BaseAppError):
    """数据验证异常"""

    status_code = 422
    error_code = "validation_error"
    message = "数据验证失败"


class UnauthorizedError(BaseAppError):
    """未授权异常"""

    status_code = 401
    error_code = "unauthorized"
    message = "用户未授权"


class ForbiddenError(BaseAppError):
    """禁止访问异常"""

    status_code = 403
    error_code = "forbidden"
    message = "禁止访问此资源"


class EntityNotFoundError(ResourceNotFoundError):
    """实体未找到异常"""

    error_code = "entity_not_found"
    message = "请求的实体不存在"

    def __init__(
        self,
        entity_name: str | None = None,
        entity_id: str | None = None,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        # 如果提供了实体名称和 ID，但没有提供 message，则自动生成 message
        if not message and entity_name and entity_id:
            message = f"Entity not found: {entity_name} with id {entity_id}"

        # 如果提供了实体名称和 ID，但没有提供详情，则生成详情
        if entity_name and entity_id and not details:
            details = {"entity": entity_name, "id": entity_id}

        super().__init__(message=message, details=details)


class BadRequestError(BaseAppError):
    """错误请求异常"""

    status_code = 400
    error_code = "bad_request"
    message = "错误的请求"


class RateLimitExceededError(BaseAppError):
    """速率限制异常"""

    status_code = 429
    error_code = "rate_limit_exceeded"
    message = "请求频率超过限制"

    def __init__(
        self,
        retry_after: int | None = None,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        headers = {"Retry-After": str(retry_after)} if retry_after else None

        if retry_after and not details:
            details = {"retry_after_seconds": retry_after}

        super().__init__(message=message, details=details, headers=headers)


class TaskNotFoundError(ResourceNotFoundError):
    """任务未找到异常"""

    error_code = "task_not_found"
    message = "未找到任务"

    def __init__(self, task_id: str, details: dict[str, Any] | None = {}):
        message = f"{self.message}: task_id={task_id}"
        details.update({"task_id": task_id})
        super().__init__(message=message, details=details)
