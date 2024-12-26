import json
from typing import Dict, Any, Annotated

from rabbit.base_aio import ServiceConsumer
import logging
from api.user_v1 import users_crud
from core.models import db_helper
from core.models.user_model import User

log = logging.getLogger(__name__)


class UserConsumer(ServiceConsumer):
    """
    Класс для обработки сообщений, относящихся к пользователям.
    """

    async def handle_user_request(
        self,
        message: Dict[str, Any],
    ) -> None:
        """
        Обработчик запросов на получение данных пользователя.

        :param message: Входящее сообщение из RabbitMQ.
        """
        try:
            log.warning(f"Начало обработки сообщения: {message}\nТип:")
            if isinstance(message, bytes):
                message = json.loads(message.decode("utf-8"))
            action = message.get("action")
            username = message.get("username")
            correlation_id = message.get("correlation_id")
            log.info(f"Получен запрос: action={action}, username={username} 😊")
            if action == "get_user_data" and username:
                async with db_helper.session() as session:
                    user: User = await users_crud.crud_user.get_user_by_field(
                        db=session, field="username", value=username
                    )
                    response = (
                        {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "hashed_password": user.hashed_password,
                            "is_active": user.is_active,
                            "correlation_id": correlation_id,
                        }
                        if user
                        else {"error": "Пользователь не найден"}
                    )
            else:
                response = {"error": "Неправильный запрос"}

            # Отправляем ответ обратно
            await self.reply_to_rpc_request(message, response)
            log.info("Ответ отправлен обратно успешно! 🚀")
        except Exception as e:
            log.error(f"❌ Ошибка обработки запроса: {e}")

    async def process_auth_events(self, message: dict):
        """
        Обрабатывает события, поступающие от микросервиса `auth`.
        """
        event = message.get("event")
        data = message.get("data")

        if event == "token_issued":
            user_id = data.get("user_id")
            username = data.get("username")
            log.info(
                f"Обработано событие: токен выдан для пользователя {username} (ID: {user_id})."
            )
            # Логика обработки события
        elif event == "token_validated":
            username = data.get("username")
            log.info(
                f"Обработано событие: токен подтвержден для пользователя {username}."
            )
            # Логика обработки события
        else:
            log.warning(f"Неизвестное событие: {event}.")
