from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from aezakmi_task.utils.metrics import REQUESTS_TOTAL


class RequestCountMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
    ):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        REQUESTS_TOTAL.inc()

        # process the request and get the response
        response = await call_next(request)
        return response
