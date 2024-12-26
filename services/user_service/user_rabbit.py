import asyncio
import logging
from rabbit.aio_config import RabbitMQConfig
from user_consumer import UserConsumer

log = logging.getLogger(__name__)
"""
Должен быть определен экземпляр класса RabbitMQConfig

class RabbitMQConfig:
    def __init__(
        self,
        exchange_name: str,  # Имя основного обменника
        routing_key: str,     # Ключ маршрутизации
        dlx_name: str,       # Имя Dead Letter Exchange (DLX)
        dlx_key: str,        # Имя Dead Letter Queue (DLQ)
        connection_url: str,  # URL подключения к RabbitMQ
    ):
        self.exchange_name = exchange_name  # Сохраняем имя обменника
        self.routing_key = routing_key        # Сохраняем ключ маршрутизации
        self.dlx_name = dlx_name              # Сохраняем имя DLX
        self.dlx_key = dlx_key                # Сохраняем имя DLQ
        self.connection_url = connection_url  # Сохраняем URL подключения
"""

# Конфигурация для микросервиса `user`
user_config = RabbitMQConfig(
    # URL для подключения к RabbitMQ, включая пользователя и пароль
    connection_url="amqp://guest:guest@rabbitmq_host:5672/",
    # Имя основного обменника, который будет использоваться для отправки сообщений
    exchange_name="user_exchange",
    # Ключ маршрутизации, который определяет, как сообщения будут направляться
    routing_key="user_routing_key",
    # Имя Dead Letter Exchange (DLX), куда будут отправляться сообщения, которые не могут быть обработаны
    dlx_name="user_dlx",
    # Имя Dead Letter Queue (DLQ), куда будут помещаться сообщения, которые не были обработаны
    dlx_key="user_dlq",
)


async def start_consumer_user():
    """
    Старт консьюмера для сервиса пользователей с обработкой ошибок подключения.
    """
    try:
        await asyncio.sleep(2)
        user_consumer = UserConsumer(config=user_config)
        log.info("Консьюмер пользователя инициализирован")
        await user_consumer.consume_messages(user_consumer.handle_user_request)
    except Exception as e:
        log.error(f"Критическая ошибка consumer: {e}")
        # Можно добавить логику перезапуска или уведомления
        await asyncio.sleep(5)  # Пауза перед возможным рестартом
