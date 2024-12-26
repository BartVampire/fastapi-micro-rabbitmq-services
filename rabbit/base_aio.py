import asyncio
import json
import logging
import os
import socket
import uuid
from typing import Dict, Any, Callable, Optional, Union, List

import aio_pika
from aio_pika import IncomingMessage
from aio_pika.abc import (
    AbstractChannel,
    AbstractQueue,
    AbstractIncomingMessage,
    ExchangeType,
)

from rabbit.aio_config import RabbitMQConfig

logging.basicConfig(
    level=logging.INFO,  # Установите уровень на INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class AsyncRabbitBase:
    """
    Базовый класс для операций с RabbitMQ, использующий aio_pika.
    Предоставляет методы для управления соединениями и объявления очередей.
    """

    def __init__(self, config: RabbitMQConfig):
        """
        Инициализация базового класса.

        :param config: Конфигурация RabbitMQ для текущего сервиса.
        """
        self.config = config
        self.pending_responses: Dict[str, asyncio.Future] = (
            {}
        )  # Хранилище ожидающих ответов

    async def connect_with_retry(
        self,
        connection_url: str,
        max_retries: int = 10,
        delay: int = 5,
    ) -> aio_pika.abc.AbstractRobustConnection:
        """
        Подключение к RabbitMQ с механизмом повторных попыток.

        :param connection_url: URL для подключения
        :param max_retries: Максимальное количество попыток
        :param delay: Задержка между попытками в секундах
        :return: Соединение с RabbitMQ
        """
        log.warning(f"🔗 Попытка подключения к RabbitMQ по URL: {connection_url}")
        for attempt in range(max_retries):
            try:
                connection = await aio_pika.connect_robust(connection_url)
                log.warning(
                    f"✅ Успешное подключение к RabbitMQ (попытка {attempt + 1})"
                )
                return connection
            except Exception as e:
                log.warning(
                    f"⚠️ Ошибка подключения к RabbitMQ (попытка {attempt + 1}/{max_retries}): {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay)
                else:
                    log.error(
                        "❌ Не удалось подключиться к RabbitMQ после всех попыток"
                    )
                    raise

    async def get_connection(self) -> aio_pika.abc.AbstractRobustConnection:
        """
        Установить соединение с RabbitMQ.

        :return: Объект соединения aio_pika.RobustConnection.
        """
        # return await aio_pika.connect_robust(self.config.connection_url)
        return await self.connect_with_retry(self.config.connection_url)

    async def declare_infrastructure(
        self,
        channel: AbstractChannel,
        additional_bindings: Optional[List[Dict[str, str]]] = None,
    ) -> AbstractQueue:
        """
        Объявить инфраструктуру RabbitMQ: DLX, DLQ, основной обменник и очередь.
        :param channel: Канал для декларации объектов.
        :param additional_bindings: Список дополнительных привязок.
        :return: Объект основной очереди.
        """
        # Объявляем Dead Letter Exchange (DLX)
        dlx_exchange = await channel.declare_exchange(
            self.config.dlx_name,
            aio_pika.ExchangeType.FANOUT,
            durable=False,  # Durable (это сохраняет обменник в хранилище)
        )
        log.info(
            f"✅ DLX (Dead Letter Exchange) объявлен: {dlx_exchange.name}\n🔺 Это обменник для обработки сообщений, которые не могут быть доставлены.🔻\n"
        )

        # Объявляем Dead Letter Queue (DLQ)
        dlq = await channel.declare_queue(self.config.dlx_key, durable=False)
        await dlq.bind(dlx_exchange)
        log.info(
            f"🔗 DLQ (Dead Letter Queue) объявлена и привязана: {dlq.name}\n🔺 Это очередь для хранения недоставленных сообщений.🔻\n"
        )

        # Объявляем основной обменник
        main_exchange = await channel.declare_exchange(
            self.config.exchange_name, aio_pika.ExchangeType.FANOUT, durable=False
        )
        log.info(
            f"📦 Основной обменник объявлен: {main_exchange.name}\n🔺 Это основной обменник для маршрутизации сообщений в систему.🔻\n"
        )

        # Объявляем основную очередь с привязкой к DLX
        main_queue = await channel.declare_queue(
            self.config.routing_key,
            durable=True,
            arguments={"x-dead-letter-exchange": self.config.dlx_name},
        )
        await main_queue.bind(main_exchange, routing_key=self.config.routing_key)
        log.info(
            f"📬 Основная очередь объявлена и привязана: {main_queue.name}\n🔺 Это очередь, в которую будут поступать сообщения, связанные с ключом маршрутизации.🔻\n"
        )
        # Обрабатываем дополнительные привязки
        if additional_bindings:
            for binding in additional_bindings:
                exchange_name = binding["exchange_name"]
                routing_key = binding.get("routing_key", "")
                extra_exchange = await channel.declare_exchange(
                    exchange_name, aio_pika.ExchangeType.FANOUT, durable=False
                )
                await main_queue.bind(extra_exchange, routing_key=routing_key)
                log.info(
                    f"🔗 Очередь {main_queue.name} привязана к обменнику {exchange_name} "
                    f"с ключом маршрутизации '{routing_key}'"
                )
                log.debug(f"Дополнительная привязка: {binding}")
        return main_queue


# Класс продюсера для микросервиса
class ServicePublisher(AsyncRabbitBase):
    """
    Класс для публикации сообщений в RabbitMQ для конкретного микросервиса.
    """

    async def publish_message(self, message: Dict[str, Any]) -> None:
        """
        Отправить сообщение в обменник.

        :param message: Тело сообщения в формате словаря.
        """
        connection = await self.get_connection()
        async with connection:
            channel = await connection.channel()
            await self.declare_infrastructure(channel)
            # Получаем объявленный обменник
            exchange = await channel.declare_exchange(
                self.config.exchange_name, aio_pika.ExchangeType.FANOUT, durable=False
            )
            message_body = json.dumps(message)
            log.info(
                f"📤 Отправка сообщения: {message_body}\n🔺 Сообщение будет отправлено в {self.config.exchange_name} обменник для дальнейшей обработки.🔻\n"
            )

            await exchange.publish(
                aio_pika.Message(body=message_body.encode()),
                routing_key="",
            )

    async def rpc_request(
        self,
        message: Dict[str, Any],
        exchange_name: Optional[str] = None,
        routing_key: Optional[str] = None,
        correlation_id: Optional[str] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        Отправка RPC-запроса через RabbitMQ и ожидание ответа.
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        connection = await self.get_connection()
        async with connection:
            channel = await connection.channel()
            callback_queue = await channel.declare_queue(exclusive=True)

            # Создаем future для ожидания ответа
            future = asyncio.get_event_loop().create_future()
            self.pending_responses[correlation_id] = future

            try:
                target_exchange = exchange_name or self.config.exchange_name
                target_routing_key = routing_key or self.config.routing_key

                log.info(
                    f"📤 Отправка RPC-запроса в exchange={target_exchange}, routing_key={target_routing_key}\n"
                    f"Message: {message}\nCallback: {callback_queue.name}\n с correlation_id={correlation_id}"
                )

                # Публикуем сообщение
                await channel.default_exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(message).encode(),
                        reply_to=callback_queue.name,
                        correlation_id=correlation_id,
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    ),
                    routing_key=target_routing_key,
                )

                # Ожидаем ответ
                try:
                    response = await asyncio.wait_for(future, timeout=timeout)
                    return response
                except asyncio.TimeoutError:
                    log.error(
                        f"⏳ RPC запрос истек по времени (timeout)! correlation_id={correlation_id}"
                    )
                    return {"status": "error", "message": "Request timeout"}
            finally:
                try:
                    # Убираем future из словаря
                    await self.pending_responses.pop(correlation_id, None)
                    # Удаляем временную очередь
                    await callback_queue.delete()
                except Exception as e:
                    log.error(f"Error in cleanup: {str(e)}")


# Класс потребителя для микросервиса
class ServiceConsumer(AsyncRabbitBase):
    """
    Класс для обработки сообщений из очереди RabbitMQ для конкретного микросервиса.
    """

    async def consume_messages(
        self,
        message_callback: Callable[[Dict[str, Any]], Any],
        additional_bindings: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """
        Начать обработку сообщений из очереди.
        :param additional_bindings: Список дополнительных привязок в формате:
        [{"exchange_name": "user_exchange", "routing_key": ""}, ...]
        :param message_callback: Функция обратного вызова для обработки каждого сообщения.
        """
        async with await self.get_connection() as connection:
            channel = await connection.channel()
            # Объявляем инфраструктуру (обменники, очереди, привязки)
            queue = await self.declare_infrastructure(channel, additional_bindings)

            async with queue.iterator() as queue_iter:
                log.info(
                    "👀 Ждём сообщений... ⏳ - Ожидание поступления новых сообщений в очередь для обработки."
                )
                async for raw_message in queue_iter:
                    # Явно указываем тип для IDE и обрабатываем корутину, если требуется
                    if isinstance(raw_message, AbstractIncomingMessage):
                        message: AbstractIncomingMessage = raw_message
                    else:
                        message: AbstractIncomingMessage = await raw_message

                    async with message.process():
                        try:
                            body: Dict[str, Any] = json.loads(
                                message.body.decode("utf-8")
                            )
                            log.info(f"📥 Получено сообщение: {body}")

                            # Проверяем наличие correlation_id
                            if "correlation_id" in body:
                                await self.resolve_response(body)
                            else:
                                await message_callback(body)

                        except Exception as e:
                            log.error(f"❌ Ошибка обработки сообщения: {e}")
                            raise

    async def reply_to_rpc_request(
        self, original_message: Dict[str, Any], response: Dict[str, Any]
    ) -> None:
        """
        Отправка ответа на RPC-запрос.

        :param original_message: Оригинальное сообщение
        :param response: Ответ для отправки
        """
        try:
            log.info(f"----- Отправка ответа: {response}")
            # Преобразуем данные в response в JSON-совместимый формат
            for key, value in response.items():
                if isinstance(value, bytes):
                    response[key] = value.decode("utf-8")
            async with await self.get_connection() as connection:
                async with connection:
                    channel = await connection.channel()
                    # Проверьте, что response сериализуем в JSON
                    if isinstance(response, bytes):
                        response = json.loads(response.decode("utf-8"))
                    log.info(
                        f'📤 Отправка ответа: {response}, correlation_id={original_message.get("correlation_id")}, reply_to={original_message.get("reply_to")}'
                    )
                    await channel.default_exchange.publish(
                        aio_pika.Message(
                            body=json.dumps(response).encode("utf-8"),
                            correlation_id=original_message.get(
                                "correlation_id"
                            ),  # Устанавливаем корреляционный ID
                        ),
                        routing_key=original_message.get("reply_to", ""),
                    )
        except Exception as e:
            log.error(f"Ошибка отправки ответа: {e}")

    async def resolve_response(self, message: Union[IncomingMessage, Dict[str, Any]]):
        if isinstance(message, IncomingMessage):
            correlation_id = message.correlation_id
            body = json.loads(message.body.decode())
        elif isinstance(message, dict):
            correlation_id = message.get("correlation_id")
            body = message
        else:
            raise ValueError("Неизвестный тип сообщения!")

        log.info(f"📥 Получен ответ с correlation_id={correlation_id}")

        if correlation_id and correlation_id in self.pending_responses:
            future = self.pending_responses.pop(correlation_id)
            if not future.done():
                future.set_result(body)
        else:
            log.warning(
                f"❗Получен ответ с неизвестным correlation_id={correlation_id}"
            )
