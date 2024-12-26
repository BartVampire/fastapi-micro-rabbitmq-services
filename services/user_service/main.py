import asyncio
import os
import uvicorn
from dotenv import load_dotenv
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.wsgi import WSGIMiddleware
from api import router as api_router

from core.config import settings
from create_fastapi_app import create_app
from core.models import db_helper
from jinja2_main import router as jinja2_router
from fastapi.staticfiles import StaticFiles

load_dotenv()

middleware = [
    #     Middleware(SessionMiddleware, secret_key=os.getenv("FASTAPI__ADMIN__SECRET_KEY")),
    #     Middleware(AdminAuthMiddleware),
]

main_app = create_app(
    create_custom_static_urls=True,  # Создание статических роутеров документации (Swagger)
    middleware=middleware,
)
# Настройка CORS если нужно
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешите нужные origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Получаем абсолютный путь к директории статических файлов и медиа
static_dir = os.path.join(os.path.dirname(__file__), "static")
media_dir = os.path.join(os.path.dirname(__file__), "media")

main_app.mount(
    "/static", StaticFiles(directory=static_dir), name="static"
)  # Регистрация директории статических файлов

main_app.mount("/media", StaticFiles(directory=media_dir), name="media")

main_app.include_router(api_router)  # Регистрация роутера API в основном приложении
main_app.include_router(
    jinja2_router
)  # Регистрация роутера Jinja2 API в основном приложении


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app", reload=True, host=settings.run.host, port=settings.run.port
    )  # Запуск приложения на сервере
