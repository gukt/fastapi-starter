from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import auth_logger
from app.database.session import get_db
from app.models.models import User
from app.models.schemas import TokenData

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token
security = HTTPBearer()


class AuthService:
    """认证服务"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

        auth_logger.info(f"Access token created for user: {data.get('sub')}")
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> TokenData | None:
        """验证令牌"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("sub")
            username: str = payload.get("username")

            if user_id is None or username is None:
                auth_logger.warning("Token missing required fields")
                return None

            return TokenData(user_id=UUID(user_id), username=username)

        except JWTError as e:
            auth_logger.warning(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            auth_logger.error(f"Token verification error: {e}")
            return None

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> User | None:
        """验证用户"""
        try:
            result = await db.execute(select(User).where(User.email == email, User.is_active == True))
            user = result.scalar_one_or_none()

            if not user:
                auth_logger.warning(f"User not found: {email}")
                return None

            if not AuthService.verify_password(password, user.hashed_password):
                auth_logger.warning(f"Invalid password for user: {email}")
                return None

            # 更新最后登录时间
            user.last_login = datetime.utcnow()
            await db.commit()

            auth_logger.info(f"User authenticated successfully: {email}")
            return user

        except Exception as e:
            auth_logger.error(f"Authentication error: {e}")
            return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 验证令牌
        token_data = AuthService.verify_token(credentials.credentials)
        if token_data is None:
            raise credentials_exception

        # 查询用户
        result = await db.execute(select(User).where(User.id == token_data.user_id, User.is_active == True))
        user = result.scalar_one_or_none()

        if user is None:
            auth_logger.warning(f"User not found for token: {token_data.user_id}")
            raise credentials_exception

        return user

    except Exception as e:
        auth_logger.error(f"Get current user error: {e}")
        raise credentials_exception


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """获取当前超级用户"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


class PermissionChecker:
    """权限检查器"""

    def __init__(self, required_permissions: list):
        self.required_permissions = required_permissions

    def __call__(self, current_user: User = Depends(get_current_active_user)):
        # 这里可以实现更复杂的权限检查逻辑
        # 目前简单检查是否为超级用户
        if not current_user.is_superuser and self.required_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user


# 常用权限检查依赖
require_superuser = PermissionChecker(["admin"])
require_user = PermissionChecker(["user"])
