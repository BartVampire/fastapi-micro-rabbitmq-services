from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
)

from core import settings
from dotenv import load_dotenv

load_dotenv()


class DatabaseHelper:
    """
    Класс для работы с базой данных SQLAlchemy
    """

    def __init__(
        self,
        url: str,  # URL для подключения к базе данных
        echo: bool = False,  # Логирование SQL-запросов в консоль
        echo_pool: bool = False,  # Выводить логирование пула соединений
        pool_size: int = 5,  # Размер количества соединений в пуле
        max_overflow: int = 10,  # Количество превышения пула соединений
    ):
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,  # Привязка к создаваемым сессиям к базе данных
            autoflush=False,
            autocommit=False,  # Автоматически коммитить изменения в БД при закрытии сессии
            expire_on_commit=False,  # Сами следим за изменениями в БД
        )  # Создание фабрики сессий для асинхронной работы с БД

    async def dispose(self) -> None:  # Закрытие соединения с базой данных
        await self.engine.dispose()  # Закрытие подключения к БД

    async def session_getter(
        self,
    ) -> AsyncGenerator[AsyncSession, None]:  # Асинхронный генератор сессий
        async with self.session_factory() as session:  # Создание сессии
            yield session  # Возвращаем сессию в контекстный менеджер


db_helper = DatabaseHelper(
    url=str(settings.db.url),  # URL для подключения к базе данных
    echo=settings.db.echo,  # Логирование SQL-запросов в консоль
    echo_pool=settings.db.echo_pool,  # Выводить логирование пула соединений
    pool_size=settings.db.pool_size,  # Размер количества соединений в пуле
    max_overflow=settings.db.max_overflow,  # Количество превышения пула соединений
)
