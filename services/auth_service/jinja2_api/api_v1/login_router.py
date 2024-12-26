import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Request, Depends, Query
from fastapi.templating import Jinja2Templates

from api.auth_v1.auth_jwt_router import auth_user_issue_jwt
from jinja2_api.templates_jinja2 import templates

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Login"],
)


@router.get("/login")
async def login_page(request: Request):
    """
    Отображает страницу входа для аутентификации пользователя с использованием JWT 🔑.

    - **request**: Объект запроса, который передается для рендеринга шаблона 📄.

    Возвращает HTML-страницу с формой для входа 🎉.
    """
    return templates.TemplateResponse(
        "login_page.html",
        {
            "request": request,
        },
    )
