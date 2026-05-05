import json
import logging
from typing import Any, Dict

from iot_api.clients.mqtt import MQTTClient
from iot_api.clients.redis import RedisClient
from iot_api.core import config
from iot_api.helpers.mqtt import generate_status_handler
from iot_api.services.devices.base import DeviceStrategy

logger = logging.getLogger(__name__)


class CoffeeMakerStrategy(DeviceStrategy):
    def get_config(self, device_id: str, device_name: str) -> Dict[str, Any]:
        return {
            "id": device_id,
            "name": {"name": device_name},
            "type": "action.devices.types.COFFEE_MAKER",
            "traits": ["action.devices.traits.OnOff", "action.devices.traits.StatusReport"],
            "attributes": {"pausable": False},
            "willReportState": True,
        }

    async def get_status(self, redis_client: RedisClient, device_id: str) -> Dict[str, Any]:
        try:
            # Fetch both run state (on/off) and ready state (water/coffee availability)
            run_topic = config.REDIS_COFFEE_MAKER_RUN_STATUS_TOPIC.format(device_id)
            ready_topic = config.REDIS_COFFEE_MAKER_READY_STATUS_TOPIC.format(device_id)

            run_status = await redis_client.get(run_topic)
            ready_status = await redis_client.get(ready_topic)

            if run_status is None or ready_status is None:
                raise TimeoutError()

            is_started = int(run_status) == 1
            is_ready = int(ready_status) == 1

            status_report = []

            # If the machine is not ready (e.g., missing water), notify Google Home
            if not is_ready:
                status_report.append({"blocking": True, "priority": 0, "statusCode": "needsWater"})

            return {"on": is_started, "online": True, "currentStatusReport": status_report}
        except TimeoutError:
            logger.warning(f"Coffee Maker {device_id} is offline.")
            return {"on": False, "online": False}

    async def execute_command(
        self, redis_client: RedisClient, mqtt_client: MQTTClient, device_id: str, status: bool
    ) -> None:
        run_topic = config.REDIS_COFFEE_MAKER_RUN_STATUS_TOPIC.format(device_id)
        ready_topic = config.REDIS_COFFEE_MAKER_READY_STATUS_TOPIC.format(device_id)

        run_val = await redis_client.get(run_topic)
        ready_val = await redis_client.get(ready_topic)

        is_started = int(run_val) == 1 if run_val else False
        is_ready = int(ready_val) == 1 if ready_val else False

        # Attempting to turn ON a stopped machine
        if status and not is_started:
            if not is_ready:
                logger.error(f"Cannot start Coffee Maker {device_id}: needs water.")
                # This exception is caught by the router to send an error back to Google
                raise ValueError("needsWater")

        topic = config.MQTT_COFFEE_MAKER_COMMAND_TOPIC.format(device_id)
        payload = {"id": device_id, "status": 1 if status else 0}

        await mqtt_client.publish(topic, json.dumps(payload))
        logger.info(f"Command {'ON' if status else 'OFF'} sent to Coffee Maker {device_id}")

    async def setup_subscriptions(self, mqtt_client: MQTTClient, redis_client: RedisClient) -> None:
        """Subscribe to both run state and ready state updates for Coffee Makers."""

        # Handler for Run Status (On/Off)
        run_handler = generate_status_handler(redis_client, config.REDIS_COFFEE_MAKER_RUN_STATUS_TOPIC)
        await mqtt_client.subscribe(config.MQTT_COFFEE_MAKER_RUN_STATUS_TOPIC.format("+"), run_handler)

        # Handler for Ready Status (Water/Coffee availability)
        ready_handler = generate_status_handler(redis_client, config.REDIS_COFFEE_MAKER_READY_STATUS_TOPIC)
        await mqtt_client.subscribe(config.MQTT_COFFEE_MAKER_READY_STATUS_TOPIC.format("+"), ready_handler)
