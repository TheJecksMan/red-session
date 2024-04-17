from random import randint

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from redsession import ServerSessionMiddleware
from redsession.backend import RedisBackend

app = FastAPI(default_response_class=ORJSONResponse)

redis = Redis(host="192.168.1.3", protocol=3)

app.add_middleware(
    ServerSessionMiddleware, backend=RedisBackend(redis), secret_key="secret"
)


@app.get("/get_session")
async def get_session(request: Request):
    return {"session": request.session}


@app.post("/set_session")
async def set_session(request: Request):
    request.session.update({"id": 1})
    return {"session": request.session}


@app.put("/update_session")
async def update_session(request: Request):
    request.session.clear()
    request.session.update({"user_id": randint(-100, 100)})
    return {"session": request.session}


@app.delete("/delete_session")
async def delete_session(request: Request):
    request.session.clear()
    return {"session": request.session}
