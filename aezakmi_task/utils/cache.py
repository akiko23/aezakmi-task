import hashlib
import json
from functools import wraps
from typing import Any

from pydantic import BaseModel
from redis.asyncio import Redis


def cache(ttl: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis_client: Redis = kwargs.get("redis_client")
            args_str = json.dumps(args, default=str)

            # Создаём уникальный ключ кэша на основе имени функции и аргументов
            kwargs_for_key = kwargs.copy()
            kwargs_for_key.pop("redis_client")
            kwargs_for_key.pop("service")
            kwargs_str = json.dumps(kwargs_for_key, default=str)
            cache_key = hashlib.md5(f"{func.__name__}:{args_str}:{kwargs_str}".encode()).hexdigest()

            # Проверяем наличие в кэше
            cached_result = await redis_client.get(cache_key)
            print('Cached key: ', cache_key, '; value:', cached_result)
            if cached_result:
                print('Got cached result')
                return _load_json_value(cached_result)

            # Выполняем функцию и кэшируем результат
            result = await func(*args, **kwargs)
            await redis_client.setex(cache_key, ttl, _build_json_value(result))
            return result
        return wrapper
    return decorator


def _build_json_value(value) -> str:
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            item: BaseModel
            result.append(item.model_dump_json())
        return json.dumps(result, default=str)

    return json.dumps(value.model_dump_json(), default=str)


def _load_json_value(value) -> Any:
    obj = json.loads(value)
    if isinstance(obj, list):
        result = []
        for item in obj:
            print(item)
            result.append(json.loads(item))
        return result

    result = json.loads(obj)
    return result
