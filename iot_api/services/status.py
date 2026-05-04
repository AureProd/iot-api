import json

from iot_api.clients.redis import RedisClient
from iot_api.core import config

def handle_led_status(redis_client: RedisClient):
    async def _handle(payload: str):
        data: dict = json.loads(payload)
        led_id = data.get("id")
        status = bool(data.get("status"))
        
        await save_led_status(redis_client, led_id, status)
        
    return _handle

async def save_led_status(redis_client: RedisClient, led_id: str, status: bool):
    topic = config.REDIS_LED_STATUS_TOPIC.format(led_id)
    await redis_client.set(topic, 1 if status else 0, 300) # TTL of 5m

async def get_led_status(redis_client: RedisClient, led_id: str) -> bool:
    topic = config.REDIS_LED_STATUS_TOPIC.format(led_id)
    status = await redis_client.get(topic)
    
    if status is None:
        raise TimeoutError(f"Led device with ID '{led_id}' is not connected.")
    return int(status) == 1

def handle_coffee_maker_run_status(redis_client: RedisClient):
    async def _handle(payload: str):
        data: dict = json.loads(payload)
        coffee_maker_id = data.get("id")
        status = bool(data.get("status"))
        
        await save_coffee_maker_run_status(redis_client, coffee_maker_id, status)
        
    return _handle

async def save_coffee_maker_run_status(redis_client: RedisClient, coffee_maker_id: str, status: bool):
    topic = config.REDIS_COFFEE_MAKER_RUN_STATUS_TOPIC.format(coffee_maker_id)
    await redis_client.set(topic, 1 if status else 0, 300) # TTL of 5m

async def get_coffee_maker_run_status(redis_client: RedisClient, coffee_maker_id: str) -> bool:
    topic = config.REDIS_COFFEE_MAKER_RUN_STATUS_TOPIC.format(coffee_maker_id)
    status = await redis_client.get(topic)
    
    if status is None:
        raise TimeoutError(f"Coffee maker device with ID '{coffee_maker_id}' is not connected.")
    return int(status) == 1

def handle_coffee_maker_ready_status(redis_client: RedisClient):
    async def _handle(payload: str):
        data: dict = json.loads(payload)
        coffee_maker_id = data.get("id")
        status = bool(data.get("status"))
        
        await save_coffee_maker_ready_status(redis_client, coffee_maker_id, status)
        
    return _handle

async def save_coffee_maker_ready_status(redis_client: RedisClient, coffee_maker_id: str, status: bool):
    topic = config.REDIS_COFFEE_MAKER_RUN_STATUS_TOPIC.format(coffee_maker_id)
    await redis_client.set(topic, 1 if status else 0, 300) # TTL of 5m

async def get_coffee_maker_ready_status(redis_client: RedisClient, coffee_maker_id: str) -> bool:
    topic = config.REDIS_COFFEE_MAKER_RUN_STATUS_TOPIC.format(coffee_maker_id)
    status = await redis_client.get(topic)
    
    if status is None:
        raise TimeoutError(f"Coffee maker device with ID '{coffee_maker_id}' is not connected.")
    return int(status) == 1
