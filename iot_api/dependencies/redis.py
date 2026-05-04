from fastapi import Request

from iot_api.clients.redis import RedisClient


def get_redis_client(request: Request) -> RedisClient:
    return request.app.state.redis