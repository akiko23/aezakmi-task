from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import Response

router = APIRouter()


@router.get("/metrics")
async def metrics(_: Request) -> Response:
    return Response(generate_latest(), headers={'Content-Type': CONTENT_TYPE_LATEST})
