from fastapi import APIRouter

from .auth_v1 import auth_router

router = APIRouter()

router.include_router(auth_router)
