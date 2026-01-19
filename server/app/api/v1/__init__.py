from fastapi import APIRouter
from app.api.v1 import auth, repositories

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["Repositories"])