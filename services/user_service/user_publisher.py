import logging
from enum import Enum
from typing import Dict, Any

from rabbit.base_aio import ServicePublisher

log = logging.getLogger(__name__)


class UserEvent(str, Enum):
    CREATED = "user.created"
    UPDATED = "user.updated"
    DELETED = "user.deleted"


class UserPublisher(ServicePublisher):
    """
    Класс для публикации сообщений из микросервиса `user`.
    """

    async def publish_user_event(
        self, event_type: UserEvent, user_data
    ) -> Dict[str, Any]:
        """
        Публикует событие пользователя и ждет подтверждения от auth сервиса
        """
        log.info(f"Публикация {event_type} события для пользователя {user_data}")
        message = {
            "event_type": event_type,
            "user_data": {
                **user_data.dict(),
                "hashed_password": user_data.hashed_password.decode(),  # конвертируем bytes в строку для JSON
            },
        }

        # Отправляем сообщение
        try:
            await self.publish_message(message)
            log.info(
                f"✅ Сообщение {message} успешно отправлено в обменник {self.config.exchange_name}"
            )
        except Exception as e:
            log.error(f"❌ Ошибка отправки сообщения {message}: {str(e)}")
            # Возвращаем ошибку вместо raise, чтобы не прерывать создание пользователя
            return {
                "status": "error",
                "message": f"Failed to sync with auth service: {str(e)}",
            }
