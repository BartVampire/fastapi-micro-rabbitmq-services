import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi_limiter import FastAPILimiter

from core.redis import RedisClient, get_settings
from core.models import db_helper
# from user_rabbit import start_consumer_user

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Асинхронный контекстный менеджер для управления жизненным циклом приложения.

    Данный контекстный менеджер предназначен для обработки запуска и завершения работы приложения.
    Он используется в приложении FastAPI путем передачи его экземпляра в качестве параметра `lifespan` при инициализации.

    Параметры:
    app (FastAPI): Экземпляр приложения FastAPI, для которого требуется управление жизненным циклом.

    """

    # Запуск приложения

    # Инициализируем пул соединений при запуске
    # await RedisClient.init_pool(get_settings())
    # rediska = await RedisClient.get_client(get_settings())
    # await FastAPILimiter.init(rediska)
    # user_consumer_task = asyncio.create_task(start_consumer_user())
    log.info("Запуск консьюмера пользователя... Done! :D")

    yield
    # Остановка приложения

    print("Завершение приложения... stopping server... Done!  :D")
    # Закрываем соединения при остановке
    # await RedisClient.close()
    await db_helper.dispose()  # Закрытие соединения с базой данных
    # Завершение задачи консьюмера
    # user_consumer_task.cancel()  # Отмена задачи
    # try:
    #     await user_consumer_task  # Ожидание завершения задачи
    # except asyncio.CancelledError:
    #     pass  # Игнорируем ошибку отмены


def register_static_docs_routes(app: FastAPI):
    """
    Регистрирует статические маршруты для документации Swagger UI и ReDoc.

    Параметры:
    app (FastAPI): Экземпляр приложения FastAPI, для которого будут зарегистрированы маршруты.

    Возвращает:
    None. Функция регистрирует маршруты и не возвращает никакого значения.
    """

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        """
        Возвращает пользовательскую страницу HTML для Swagger UI.

        Этот маршрут использует функцию `get_swagger_ui_html` из FastAPI для генерации пользовательской страницы HTML для Swagger UI.
        Страница включает указанный заголовок, URL-адрес перенаправления OAuth2, а также пользовательские URL-адреса JavaScript и CSS.

        Возвращает:
        Response: Ответ FastAPI, содержащий пользовательскую страницу HTML для Swagger UI.
        """
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        """
        Возвращает ответ перенаправления для URL-адреса перенаправления OAuth2 Swagger UI.

        Этот маршрут использует функцию `get_swagger_ui_oauth2_redirect_html` из FastAPI для генерации ответа перенаправления.

        Возвращает:
        Response: Ответ FastAPI, содержащий перенаправление на URL-адрес перенаправления OAuth2.
        """
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        """
        Возвращает страницу HTML для ReDoc.

        Этот маршрут использует функцию `get_redoc_html` из FastAPI для генерации страницы HTML для ReDoc.
        Страница включает указанный заголовок и пользовательский URL-адрес JavaScript.

        Возвращает:
        Response: Ответ FastAPI, содержащий страницу HTML для ReDoc.
        """
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
        )


def create_app(
    create_custom_static_urls: bool = False,
    middleware: list = None,
) -> FastAPI:
    """
    Создает и настраивает экземпляр приложения FastAPI с опциональной регистрацией статических роутеров документации.

    Параметры:
    create_custom_static_urls (bool): Определяет, следует ли зарегистрировать статические роутеры документации.
        Если True, то регистрируются статические роутеры документации Swagger UI и ReDoc.
        Если False (по умолчанию), то документация Swagger UI и ReDoc не регистрируются.

    middleware (list): Список middleware для добавления в приложение.


    Возвращает:
    FastAPI: Экземпляр приложения FastAPI с настроенными параметрами и, при необходимости, зарегистрированными статическими роутерами документации.
    """

    app = FastAPI(
        default_response_class=ORJSONResponse,  # Использование ORJSONResponse для ускорения отправки JSON
        lifespan=lifespan,
        docs_url=(
            None if create_custom_static_urls else "/docs"
        ),  # Не показывать документацию по умолчанию
        redoc_url=(
            None if create_custom_static_urls else "/redoc"
        ),  # Не показывать ReDoc по умолчанию
        middleware=middleware,
    )  # Инициализация FastAPI

    if create_custom_static_urls:
        register_static_docs_routes(
            app
        )  # Регистрация статических роутеров документации

    return app
