import logging
import aio_pika

# DEFAULT_LOG_FORMAT = "[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s"
DEFAULT_LOG_FORMAT = "[%(module)s:%(lineno)d %(levelname)-6s - %(message)s"


# Конфигурация RabbitMQ
class RabbitMQConfig:
    def __init__(
        self,
        exchange_name: str,  # Имя основного обменника
        routing_key: str,  # Ключ маршрутизации
        dlx_name: str,  # Имя Dead Letter Exchange (DLX)
        dlx_key: str,  # Имя Dead Letter Queue (DLQ)
        connection_url: str,  # URL подключения к RabbitMQ
    ):
        """
        Конфигурация RabbitMQ для микросервиса.

        :param exchange_name: Имя основного обменника.
        :param routing_key: Ключ маршрутизации.
        :param dlx_name: Имя Dead Letter Exchange (DLX).
        :param dlx_key: Имя Dead Letter Queue (DLQ).
        :param connection_url: URL подключения к RabbitMQ.
        """
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.dlx_name = dlx_name
        self.dlx_key = dlx_key
        self.connection_url = connection_url


# Общая конфигурация для подключения к RabbitMQ
BASE_RABBITMQ_URL = "amqp://guest:guest@localhost/"


#
#
# def get_connection() -> pika.BlockingConnection:
#     """
#     Функция возвращает подключение к RabbitMQ серверу с заданными параметрами
#     """
#     return pika.BlockingConnection(parameters=connection_params)


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        datefmt="%d-%m-%Y %H:%M:%S",
        format=DEFAULT_LOG_FORMAT,
    )
