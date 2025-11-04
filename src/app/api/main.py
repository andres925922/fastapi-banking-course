from fastapi import APIRouter

from api.routes.home import home_router

api_router = APIRouter()
api_router.include_router(home_router)