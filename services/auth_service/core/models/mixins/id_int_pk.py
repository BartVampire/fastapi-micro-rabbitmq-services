from sqlalchemy.orm import Mapped, mapped_column


class IdIntPrimaryKeyMixin:  #  Класс для добавления первичного ключа (Primary Key) в модели
    id: Mapped[int] = mapped_column(primary_key=True)  # Первичный ключ (Primary Key)
