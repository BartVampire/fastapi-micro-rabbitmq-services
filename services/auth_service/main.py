import os

import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router
from core.config import settings
from create_fastapi_app import create_app
from jinja2_api import router as jinja2_api_router

main_app = create_app(
    create_custom_static_urls=True  # Создание статических роутеров документации (Swagger)
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
)  # Монтирование статических роутеров

# Монтируем папку media для доступа к файлам
main_app.mount("/media", StaticFiles(directory=media_dir), name="media")

main_app.include_router(api_router)  # Регистрация роутера API в основном приложении
main_app.include_router(jinja2_api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app", reload=True, host=settings.run.host, port=settings.run.port
    )  # Запуск приложения на сервере
