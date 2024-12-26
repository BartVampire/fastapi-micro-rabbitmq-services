import json
from typing import Any
from redis.asyncio import Redis
from sqlalchemy import inspect


def to_dict(instance):
    """
    Преобразует SQLAlchemy-модель в словарь.
    """
    return {
        c.key: getattr(instance, c.key) for c in inspect(instance).mapper.column_attrs
    }


# Функция для получения данных в Redis (будет использоваться в других модулях)
async def cache_get(redis: Redis, key: str) -> Any:
    data = await redis.get(key)
    return json.loads(data) if data else None


# Функция для сохранения данных в Redis (будет использоваться в других модулях)
async def cache_set(redis: Redis, key: str, value: Any, expire: int = 300):
    try:
        await redis.set(
            key,
            json.dumps(
                value, default=lambda x: x.dict() if hasattr(x, "dict") else str(x)
            ),
            ex=expire,
        )
    except TypeError:
        # Если есть объекты, которые все еще не могут быть сериализованы,
        # преобразуйте их в строки
        await redis.set(
            key, json.dumps({k: str(v) for k, v in value.items()}), ex=expire
        )
