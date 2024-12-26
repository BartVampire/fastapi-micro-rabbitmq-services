import uuid
from typing import Dict, Any

from auht_rabbit import auth_config
from rabbit.base_aio import ServicePublisher


class AuthPublisher(ServicePublisher):
    """
    Класс для публикации сообщений из микросервиса `auth`.
    """

    async def request_user_data(self, username: str) -> Dict[str, Any]:
        """
        Запрос данных пользователя через RabbitMQ.

        :param username: Имя пользователя.
        :return: Данные пользователя.
        """
        correlation_id = str(
            uuid.uuid4()
        )  # Уникальный ID для сопоставления запрос-ответ
        message = {
            "action": "get_user_data",
            "username": username,
            "reply_to": auth_config.routing_key,
            "correlation_id": correlation_id,
        }
        # Если запрос идёт к user_exchange, передаём exchange_name и routing_key явно
        response = await self.rpc_request(
            message=message,
            exchange_name="user_exchange",  # Используйте имя обменника для сервиса user
            routing_key="user_routing_key",  # Ключ маршрутизации для сервиса user
        )
        return response

    async def publish_token_issued(self, user_id: int, username: str):
        """
        Публикует событие выдачи токена.
        """
        message = {
            "event": "token_issued",
            "data": {"user_id": user_id, "username": username},
        }
        await self.publish_message(message)

    async def publish_token_validated(self, username: str):
        """
        Публикует событие валидации токена.
        """
        message = {
            "event": "token_validated",
            "data": {"username": username},
        }
        await self.publish_message(message)


auth_publisher = AuthPublisher(config=auth_config)
