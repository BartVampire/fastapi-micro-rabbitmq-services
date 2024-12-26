import json
import logging
from enum import Enum
from typing import Dict, Any

import aio_pika
from aio_pika import IncomingMessage
from pydantic import ValidationError

from core.schemas.auth_user_schemas import AuthUserSchema
from rabbit.base_aio import ServiceConsumer
from core.models import db_helper
from api.user_v1.users_crud import crud_user

log = logging.getLogger(__name__)


class UserEvent(str, Enum):
    CREATED = "user.created"
    UPDATED = "user.updated"
    DELETED = "user.deleted"


class AuthConsumer(ServiceConsumer):
    """
    Класс для обработки сообщений, относящихся к аутентификации.
    """

    async def initialize(self):
        """
        Инициализация консьюмера (объявление очередей и привязка к обменникам)
        """
        await self.consume_messages(
            self.process_user_event,
            additional_bindings=[
                {"exchange_name": "user_exchange", "routing_key": "auth_routing_key"}
            ],
        )

    async def process_user_event(self, message_data: Dict[str, Any]):
        """
        Обрабатывает события пользователя и возвращает результат
        """
        try:
            # Получаем данные из декодированного сообщения
            event_type = message_data.get("event_type")
            user_data = message_data.get("user_data")

            if not event_type or not user_data:
                raise ValueError("Неполные данные в сообщении")

            log.info(
                f"📥 Получено сообщение: {message_data}, тип: {type(message_data)}"
            )

            # Конвертируем строку обратно в bytes для хеша пароля
            if "hashed_password" in user_data:
                user_data["hashed_password"] = user_data["hashed_password"].encode()

            # Создаем объект схемы
            try:
                user = AuthUserSchema(**user_data)
            except ValidationError as ve:
                log.error(f"❌ Ошибка валидации данных пользователя: {str(ve)}")
                return

            result = await self.handle_user_event(event_type, user)

            # Логируем успешную операцию
            log.info(
                f"✅ Успешно обработано {event_type} событие для пользователя {user.username}"
            )

            return result

        except Exception as e:
            log.error(f"❌ Ошибка обработки сообщения: {str(e)}")
            raise

    async def handle_user_event(
        self, event_type: str, user: AuthUserSchema
    ) -> Dict[str, Any]:
        """
        Обрабатывает различные типы событий пользователя
        """
        async with db_helper.session_factory() as db:
            try:
                if event_type == UserEvent.CREATED:
                    result = await crud_user.create_user(db=db, user=user)
                elif event_type == UserEvent.UPDATED:
                    db_user = await crud_user.get_user_by_field(
                        db=db, field="username", value=user.username
                    )
                    if not db_user:
                        raise ValueError(f"Пользователь не найден: {user.username}")
                    result = await crud_user.update_user(
                        db=db, db_user=db_user, user_update=user
                    )
                elif event_type == UserEvent.DELETED:
                    db_user = await crud_user.get_user_by_field(
                        db=db, field="username", value=user.username
                    )
                    if not db_user:
                        raise ValueError(f"Пользователь не найден: {user.username}")
                    result = await crud_user.delete_user(db=db, user_uuid=db_user.uuid)
                else:
                    raise ValueError(f"Неизвестное событие: {event_type}")

                return result
            except Exception as e:
                log.error(f"❌ Ошибка при работе с БД: {str(e)}")
                raise
