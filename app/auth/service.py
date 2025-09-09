"""Auth 模块的服务层"""

import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.schemas import TokenData
from app.core.config import settings

logger = logging.getLogger("auth")
security_settings = settings.security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=security_settings.access_token_expire_minutes
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            security_settings.secret_key,
            algorithm=security_settings.algorithm,
        )

        logger.info(f"Access token created for user: {data.get('sub')}")
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> TokenData | None:
        """验证令牌"""
        try:
            payload = jwt.decode(
                token,
                security_settings.secret_key,
                algorithms=[security_settings.algorithm],
            )
            user_id: str = payload.get("sub")
            username: str = payload.get("username")

            if user_id is None or username is None:
                logger.warning("Token missing required fields")
                return None

            return TokenData(user_id=UUID(user_id), username=username)

        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email: str, password: str
    ) -> User | None:
        """验证用户"""
        try:
            result = await db.execute(
                select(User).where(User.email == email, User.is_active is True)
            )
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(f"User not found: {email}")
                return None

            if not AuthService.verify_password(password, user.hashed_password):
                logger.warning(f"Invalid password for user: {email}")
                return None

            # 更新最后登录时间
            user.last_login = datetime.now(UTC)
            await db.commit()

            logger.info(f"User authenticated successfully: {email}")
            return user

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
