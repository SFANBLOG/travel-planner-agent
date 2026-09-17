"""API 路由聚合（统一前缀 /api）"""
from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.spots import router as spots_router
from app.api.agent import router as agent_router
from app.api.trips import router as trips_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(spots_router)
api_router.include_router(agent_router)
api_router.include_router(trips_router)
