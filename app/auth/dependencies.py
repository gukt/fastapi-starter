"""Auth 模块的依赖项"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.service import AuthService
from app.database.session import get_db

# JWT Bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """获取当前用户"""
    from app.auth.exceptions import AuthenticationError

    try:
        # 验证令牌
        token_data = AuthService.verify_token(credentials.credentials)
        if token_data is None:
            raise AuthenticationError("Could not validate credentials")

        # 查询用户
        from sqlalchemy import select

        result = await db.execute(
            select(User).where(User.id == token_data.user_id, User.is_active == True)
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise AuthenticationError("User not found")

        return user

    except Exception as e:
        if isinstance(e, AuthenticationError):
            raise
        raise AuthenticationError("Authentication failed")


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """获取当前超级用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


class PermissionChecker:
    """权限检查器"""

    def __init__(self, required_permissions: list):
        self.required_permissions = required_permissions

    def __call__(self, current_user: User = Depends(get_current_active_user)):
        from app.auth.exceptions import InsufficientPermissionsError

        # 这里可以实现更复杂的权限检查逻辑
        # 目前简单检查是否为超级用户
        if not current_user.is_superuser and self.required_permissions:
            raise InsufficientPermissionsError("Insufficient permissions")
        return current_user


# 常用权限检查依赖
require_superuser = PermissionChecker(["admin"])
require_user = PermissionChecker(["user"])
