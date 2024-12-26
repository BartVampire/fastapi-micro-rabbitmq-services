from sqlalchemy.orm import Mapped, mapped_column


class IdIntPrimaryKeyMixin:  #  Класс для добавления первичного ключа (Primary Key) в модели
    """
    .id: Mapped[int]: Аннотация типа, указывающая, что id будет иметь тип int.
    .autoincrement=True: Значение этого столбца будет автоматически увеличиваться при добавлении новых записей.
    .nullable=False: Этот столбец не может содержать NULL значения.
    .unique=True: Значения в этом столбце должны быть уникальными.
    .primary_key=True: Этот столбец является первичным ключом таблицы.
    """

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
    )
