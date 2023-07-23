import pytest

from starlette.requests import Request
from starlette.testclient import TestClient
from starlette.responses import JSONResponse
from starlette.applications import Starlette

from httpx import Cookies
from fakeredis import aioredis

from redsession import ServerSessionMiddleware
from redsession.backend import RedisBackend


async def set_session(request: Request):
    request.session.update({"id": 1})
    return JSONResponse({"session": request.session})


async def get_session(request: Request):
    return JSONResponse({"session": request.session})


async def update_session(request: Request):
    request.session.clear()
    request.session.update({"user_id": 2})
    return JSONResponse({"session": request.session})


async def delete_session(request: Request):
    request.session.clear()
    return JSONResponse({"session": request.session})


@pytest.fixture
def session_app() -> Starlette:
    app = Starlette()
    app.add_route("/set_session", set_session, methods=["POST"])
    app.add_route("/get_session", get_session, methods=["GET"])
    app.add_route("/update_session", update_session, methods=["PUT"])
    app.add_route("/delete_session", delete_session, methods=["DELETE"])
    return app


def test_redis(session_app: Starlette):
    backend = RedisBackend(redis=aioredis.FakeRedis())

    session_app.add_middleware(
        ServerSessionMiddleware,
        backend=backend,
        secret_key="secret",
    )

    with TestClient(session_app) as client:
        response = client.get("/get_session")
        assert response.json() == {"session": {}}
        assert response.headers.get("Set-Cookie") is None

        response = client.post("/set_session")
        assert response.json() == {"session": {"id": 1}}
        assert response.headers.get("Set-Cookie") is not None
        assert response.cookies.get("s") is not None

        response = client.get("/get_session")
        assert response.json() == {"session": {"id": 1}}
        assert response.headers.get("Set-Cookie") is None

        response = client.put("/update_session")
        assert response.json() == {"session": {"user_id": 2}}
        assert response.headers.get("Set-Cookie") is None

        response = client.get("/get_session")
        assert response.json() == {"session": {"user_id": 2}}
        assert response.headers.get("Set-Cookie") is None

        response = client.delete("/delete_session")
        assert response.json() == {"session": {}}
        assert response.headers.get("Set-Cookie") is not None
        assert response.cookies.get("s") is None

        response = client.delete("/delete_session")
        assert response.json() == {"session": {}}
        assert response.headers.get("Set-Cookie") is None


def test_redis_uncorrect_session(session_app: Starlette):
    backend = RedisBackend(redis=aioredis.FakeRedis())

    session_app.add_middleware(
        ServerSessionMiddleware,
        backend=backend,
        secret_key="secret",
    )

    with TestClient(session_app) as client:
        uncrorrect_cookie = Cookies()
        uncrorrect_cookie.set("s", "test")

        client.cookies = uncrorrect_cookie
        response = client.get("/get_session")
        assert response.json() == {"session": {}}
        assert response.headers.get("Set-Cookie") is None
