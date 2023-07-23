from redis.asyncio import Redis

from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.applications import Starlette

from redsession import ServerSessionMiddleware
from redsession.backend import RedisBackend


redis = Redis(host="192.168.1.3")


async def get_session(request: Request):
    return JSONResponse({"session": request.session})


async def set_session(request: Request):
    request.session.update({"id": 1})
    return JSONResponse({"session": request.session})


async def update_session(request: Request):
    request.session.clear()
    request.session.update({"user_id": 2})
    return JSONResponse({"session": request.session})


async def delete_session(request: Request):
    request.session.clear()
    return JSONResponse({"session": request.session})


app = Starlette(
    routes=[
        Route("/get_session", get_session, methods=["GET"]),
        Route("/set_session", set_session, methods=["POST"]),
        Route("/update_session", update_session, methods=["PUT"]),
        Route("/delete_session", delete_session, methods=["DELETE"]),
    ]
)

app.add_middleware(
    ServerSessionMiddleware, backend=RedisBackend(redis), secret_key="secret"
)
