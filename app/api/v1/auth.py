from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthService, get_current_active_user
from app.core.decorators import handle_exceptions, handle_response
from app.core.logging import api_logger
from app.database.session import get_db
from app.models.models import User
from app.models.schemas import UserCreate, UserLogin, UserResponse, UserUpdate
from app.utils.pagination import QueryParams, get_paginated_results

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=dict, summary="用户注册")
@handle_response("用户注册成功")
@handle_exceptions()
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # 创建新用户
    hashed_password = AuthService.get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    api_logger.info(f"New user registered: {user_data.email}")
    return UserResponse.model_validate(db_user)


@router.post("/login", response_model=dict, summary="用户登录")
@handle_response("登录成功")
@handle_exceptions()
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    user = await AuthService.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60,  # 30分钟
        "user": UserResponse.model_validate(user)
    }


@router.get("/me", response_model=dict, summary="获取当前用户信息")
@handle_response()
@handle_exceptions()
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=dict, summary="更新当前用户信息")
@handle_response("用户信息更新成功")
@handle_exceptions()
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息"""
    # 检查邮箱是否已被其他用户使用
    if user_data.email and user_data.email != current_user.email:
        result = await db.execute(
            select(User).where(
                User.email == user_data.email,
                User.id != current_user.id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # 检查用户名是否已被其他用户使用
    if user_data.username and user_data.username != current_user.username:
        result = await db.execute(
            select(User).where(
                User.username == user_data.username,
                User.id != current_user.id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # 更新用户信息
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    api_logger.info(f"User updated: {current_user.email}")
    return UserResponse.model_validate(current_user)


@router.get("/users", response_model=dict, summary="获取用户列表")
@handle_response()
@handle_exceptions()
async def get_users(
    params: QueryParams = Depends(),
    search: str | None = Query(None, description="搜索邮箱或用户名"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表（需要登录）"""
    filters = {}

    # 添加搜索功能
    if search:
        filters["search"] = search

    result = await get_paginated_results(
        session=db,
        model=User,
        page=params.page,
        size=params.size,
        sort_by=params.sort_by or "created_at",
        sort_order=params.sort_order,
        search_term=search,
        search_fields=["email", "username", "full_name"]
    )

    return {
        "items": [UserResponse.model_validate(user) for user in result["items"]],
        "meta": result["meta"]
    }


@router.get("/users/{user_id}", response_model=dict, summary="获取用户详情")
@handle_response()
@handle_exceptions()
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户详情"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)
