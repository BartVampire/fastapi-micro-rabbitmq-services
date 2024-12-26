from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

from core.config import settings
from utils import camel_case_to_snake_case


class BaseModel(DeclarativeBase):
    """
    Базовая модель для всех других моделей:
    1) Метод __abstract__ для объявления модели будет считаться абстрактной.
    2) Меняем настройки для создания таблицы: naming_convention.
    3) Преобразуем имя модели в snake_case для создания таблицы и добавляем s в конце имени таблицы.
    """

    __abstract__ = True  # Модель не будет создана в базе данных

    metadata = MetaData(
        naming_convention=settings.db.naming_convention
    )  # Настройки для создания таблицы

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(cls.__name__)}s"  # Преобразуем имя модели в snake_case
