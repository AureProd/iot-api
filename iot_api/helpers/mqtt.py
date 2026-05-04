import json
import logging
from typing import Callable, Awaitable

from iot_api.clients.redis import RedisClient

logger = logging.getLogger(__name__)

def generate_status_handler(redis_client: RedisClient, redis_topic_template: str, ttl: int = 300) -> Callable[[str], Awaitable[None]]:
    """
    Generates an asynchronous handler for incoming MQTT messages.
    Parses the JSON payload and saves the boolean status to Redis.
    """
    async def _handle(payload: str):
        try:
            data = json.loads(payload)
            device_id = data.get("id")
            status = bool(data.get("status"))
            
            if device_id:
                # Format the specific Redis topic for this device
                topic = redis_topic_template.format(device_id)
                await redis_client.set(topic, 1 if status else 0, ttl)
                
        except json.JSONDecodeError:
            logger.error(f"Failed to decode MQTT payload: {payload}")
        except Exception as e:
            logger.error(f"Error handling MQTT payload: {e}")
            
    return _handle