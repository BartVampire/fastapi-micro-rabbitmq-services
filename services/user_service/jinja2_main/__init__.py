from fastapi import APIRouter

from .api import index_router

router = APIRouter()

router.include_router(index_router)
