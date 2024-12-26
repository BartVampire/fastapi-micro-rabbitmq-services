from fastapi import APIRouter

from .api_v1 import login_router

router = APIRouter()

router.include_router(login_router)