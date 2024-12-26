import asyncio
import logging
from rabbit.aio_config import RabbitMQConfig
from auth_consumer import AuthConsumer

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

# Конфигурация для микросервиса `auth`
auth_config = RabbitMQConfig(
    connection_url="amqp://guest:guest@rabbitmq_host:5672/",  # URL для подключения к RabbitMQ, включая пользователя и пароль
    exchange_name="auth_exchange",  # Имя основного обменника, который будет использоваться для отправки сообщений
    routing_key="auth_routing_key",  # Ключ маршрутизации, который определяет, как сообщения будут направляться
    dlx_name="auth_dlx",  # Имя Dead Letter Exchange (DLX), куда будут отправляться сообщения, которые не могут быть обработаны
    dlx_key="auth_dlq",  # Имя Dead Letter Queue (DLQ), куда будут помещаться сообщения, которые не были обработаны
)


async def start_consumer_auth():
    """
    Запуск консьюмера для сервиса аутентификации.
    """
    while True:  # Бесконечный цикл для перезапуска консьюмера при ошибках
        try:
            await asyncio.sleep(2)  # Пауза перед запуском
            auth_consumer = AuthConsumer(config=auth_config)
            await auth_consumer.initialize()
            log.info("Консьюмер аутентификации инициализирован")
            await auth_consumer.consume_messages(auth_consumer.process_user_event)
        except Exception as e:
            log.error(f"Критическая ошибка консьюмера аутентификации: {e}")
            log.info("Перезапуск консьюмера через 5 секунд...")
            await asyncio.sleep(5)  # Пауза перед перезапуском
