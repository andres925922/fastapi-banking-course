from fastapi import APIRouter

home_router = APIRouter(prefix="/home")

@home_router.get("/")
async def read_root():
    return {"message": "Hello, World!"}