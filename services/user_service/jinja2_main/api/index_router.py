import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Request, Depends, Query
from fastapi.templating import Jinja2Templates
from jinja2_main.jinja2_templates import templates

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Index"],
)


@router.get("/register")
async def index_page(
    request: Request,
):

    return templates.TemplateResponse(
        name="register-page.html",
        context={
            "request": request,
        },
    )
