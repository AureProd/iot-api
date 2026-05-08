import json
import logging
from typing import Any, Dict

from iot_api.clients.mqtt import MQTTClient
from iot_api.clients.redis import RedisClient
from iot_api.core import config
from iot_api.helpers.mqtt import generate_status_handler
from iot_api.services.devices.base import DeviceStrategy

logger = logging.getLogger(__name__)


class LedStrategy(DeviceStrategy):
    def get_config(self, device_id: str, device_name: str) -> Dict[str, Any]:
        # Basic Google Home configuration for a light device
        return {
            "id": device_id,
            "name": {"name": device_name},
            "type": "action.devices.types.LIGHT",
            "traits": ["action.devices.traits.OnOff"],
            "willReportState": True,
        }

    async def get_status(self, redis_client: RedisClient, device_id: str) -> Dict[str, Any]:
        try:
            topic = config.REDIS_LED_STATUS_TOPIC.format(device_id)
            status = await redis_client.get(topic)

            if status is None:
                raise TimeoutError()

            return {"on": int(status) == 1, "online": True}
        except TimeoutError:
            # Fallback when the device hasn't reported its status recently
            logger.warning(f"LED {device_id} is offline or status not found in Redis.")
            return {"on": False, "online": False}

    async def execute_command(
        self, redis_client: RedisClient, mqtt_client: MQTTClient, device_id: str, target_state_type: str, status: bool
    ) -> dict[str, Any]:
        if target_state_type != "OnOff":
            raise ValueError("actionNotAvailable")

        logger.info(f"Sending command to LED {device_id}: {'ON' if status else 'OFF'}")
        topic = config.MQTT_LED_COMMAND_TOPIC.format(device_id)

        payload = {"id": device_id, "status": 1 if status else 0}

        await mqtt_client.publish(topic, json.dumps(payload))

        return {"on": status, "online": True}

    async def setup_subscriptions(self, mqtt_client: MQTTClient, redis_client: RedisClient) -> None:
        """Subscribe to LED status updates from MQTT."""
        handler = generate_status_handler(redis_client, config.REDIS_LED_STATUS_TOPIC)
        # Use the "+" wildcard to listen to all LEDs
        await mqtt_client.subscribe(config.MQTT_LED_STATUS_TOPIC.format("+"), handler)
