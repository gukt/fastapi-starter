from fastapi import APIRouter, Depends
from app.api.v1 import auth, posts

api_router = APIRouter()

# +@	v1ï1
api_router.include_router(auth.router)
api_router.include_router(posts.router)