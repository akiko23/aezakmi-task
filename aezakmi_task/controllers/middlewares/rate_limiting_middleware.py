import time
from contextlib import suppress

from dishka import AsyncContainer
from fastapi import HTTPException
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Настройки rate limiting
RATE_LIMIT = 50  # Максимум 50 запросов
TIME_WINDOW = 60  # Временное окно в секундах (1 минута)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, ioc_container: AsyncContainer):
        super().__init__(app)
        self._ioc_container = ioc_container
        self._cache = {}

    async def dispatch(self, request: Request, call_next):
        redis_client = await self._ioc_container.get(Redis)

        client_ip = request.client.host
        redis_key = f"ratelimit:{client_ip}"

        try:
            current_count = await redis_client.get(redis_key)
            if not current_count:
                await redis_client.setex(redis_key, RATE_LIMIT, 1)
                response = await call_next(request)
                return response

            current_count = await redis_client.incr(redis_key)
            print(f"{redis_key}: {current_count}")

            if int(current_count) > RATE_LIMIT:
                if not self._cache.get(redis_key):
                    self._cache[redis_key] = time.time()

                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too Many requests"},
                    headers={"Retry-After": str(TIME_WINDOW - (time.time() - self._cache[redis_key])),}
                )

            with suppress(KeyError):
                del self._cache[redis_key]

            response = await call_next(request)
            return response
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Internal Server Error: {str(e)}"},
            )
