from fastapi import HTTPException

from iot_api.clients.redis import RedisClient
from iot_api.core import config


async def save_oauth_code(redis_client: RedisClient, code: str, user_email: str):
    topic = config.REDIS_OAUTH_CODE_TOPIC.format(code)
    await redis_client.set(topic, user_email, 600) # TTL of 10m
    
async def get_user_from_oauth_code(redis_client: RedisClient, code: str) -> str:
    topic = config.REDIS_OAUTH_CODE_TOPIC.format(code)
    user_email = await redis_client.pop(topic)
    if not user_email:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    return user_email
    
async def save_refresh_token(redis_client: RedisClient, token: str, user_email: str):   
    topic = config.REDIS_OAUTH_REFRESH_TOPIC.format(token)
    await redis_client.set(topic, user_email, 2592000) # TTL of 30d

async def get_user_from_refresh_token(redis_client: RedisClient, token: str) -> str:
    topic = config.REDIS_OAUTH_REFRESH_TOPIC.format(token)
    user_email = await redis_client.get(topic)
    if not user_email:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    return user_email