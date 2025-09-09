from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.posts.router import router as posts_router

api_router = APIRouter()

# 注册路由
api_router.include_router(auth_router)
api_router.include_router(posts_router)
