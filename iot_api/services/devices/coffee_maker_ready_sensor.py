import logging
from typing import Any, Dict

from iot_api.clients.mqtt import MQTTClient
from iot_api.clients.redis import RedisClient
from iot_api.core import config
from iot_api.services.devices.base import DeviceStrategy

logger = logging.getLogger(__name__)


class CoffeeMakerReadySensorStrategy(DeviceStrategy):
    def get_config(self, device_id: str, device_name: str) -> Dict[str, Any]:
        return {
            "id": device_id,
            "name": {"name": device_name},
            "type": "action.devices.types.SENSOR",
            "traits": [
                "action.devices.traits.SensorState",
            ],
            "willReportState": True,
            "attributes": {
                "sensorStatesSupported": [
                    {"name": "CoffeeReady", "descriptiveCapabilities": {"availableStates": ["ready", "not_ready"]}}
                ],
            },
        }

    async def get_status(self, redis_client: RedisClient, device_id: str) -> Dict[str, Any]:
        try:
            base_device_id = device_id.replace("-status", "")

            ready_topic = config.REDIS_COFFEE_MAKER_READY_STATUS_TOPIC.format(base_device_id)
            ready_status = await redis_client.get(ready_topic)

            if ready_status is None:
                raise TimeoutError()

            is_ready = int(ready_status) == 1
            sensor_state_value = "ready" if is_ready else "not_ready"

            return {
                "online": True,
                "currentSensorStateData": [{"name": "CoffeeReady", "currentSensorState": sensor_state_value}],
            }
        except TimeoutError:
            logger.warning(f"Sensor {device_id} is offline.")
            return {"online": False}

    async def execute_command(
        self, redis_client: RedisClient, mqtt_client: MQTTClient, device_id: str, status: bool
    ) -> None:
        # Un capteur est en lecture seule, il ne peut pas recevoir de commandes EXECUTE
        logger.error(f"Cannot execute command on a SENSOR device ({device_id}).")
        raise ValueError("notSupported")

    async def setup_subscriptions(self, mqtt_client: MQTTClient, redis_client: RedisClient) -> None:
        # On met 'pass' car la classe principale CoffeeMakerStrategy gère déjà
        # la souscription MQTT -> Redis pour ces topics.
        pass
