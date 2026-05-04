import json
import logging
from typing import Dict, Any
from iot_api.services.devices.base import DeviceStrategy
from iot_api.clients.mqtt import MQTTClient
from iot_api.clients.redis import RedisClient
from iot_api.core import config

logger = logging.getLogger(__name__)

class LedStrategy(DeviceStrategy):
    def get_config(self, device_id: str, device_name: str) -> Dict[str, Any]:
        return {
            "id": device_id,
            "name": {"name": device_name},
            "type": "action.devices.types.LIGHT",
            "traits": ["action.devices.traits.OnOff"],
            "willReportState": True
        }

    async def get_status(self, redis_client: RedisClient, device_id: str) -> Dict[str, Any]:
        try:
            topic = config.REDIS_LED_STATUS_TOPIC.format(device_id)
            status = await redis_client.get(topic)
            if status is None:
                raise TimeoutError()
            return {"on": int(status) == 1, "online": True}
        except TimeoutError:
            logger.warning(f"LED {device_id} is offline or status not found in Redis.")
            return {"on": False, "online": False}

    async def execute_command(self, redis_client: RedisClient, mqtt_client: MQTTClient, device_id: str, status: bool) -> None:
        logger.info(f"Sending command to LED {device_id}: {'ON' if status else 'OFF'}")
        topic = config.MQTT_LED_COMMAND_TOPIC.format(device_id)
        payload = {"id": device_id, "status": 1 if status else 0}
        await mqtt_client.publish(topic, json.dumps(payload))