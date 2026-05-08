import logging
from abc import ABC, abstractmethod
from typing import Any

from iot_api.clients.mqtt import MQTTClient
from iot_api.clients.redis import RedisClient

logger = logging.getLogger(__name__)


class DeviceStrategy(ABC):
    """
    Abstract base class for all device types.
    Enforces a strict contract that every new device must follow.
    """

    @abstractmethod
    def get_config(self, device_id: str, device_name: str) -> dict[str, Any]:
        """
        Returns the configuration required for Google Smart Home SYNC intent.
        """
        pass

    @abstractmethod
    async def get_status(self, redis_client: RedisClient, device_id: str) -> dict[str, Any]:
        """
        Retrieves the current state of the device for the QUERY intent.
        """
        pass

    @abstractmethod
    async def execute_command(
        self, redis_client: RedisClient, mqtt_client: MQTTClient, device_id: str, target_state_type: str, status: bool
    ) -> dict[str, Any]:
        """
        Executes an On/Off command to change the device state.
        Should raise a ValueError with a specific error code (e.g., 'needsWater') if blocked.
        """
        pass

    @abstractmethod
    async def setup_subscriptions(self, mqtt_client: MQTTClient, redis_client: RedisClient) -> None:
        """
        Subscribes to the necessary MQTT topics for this specific device type
        and registers the appropriate callbacks.
        """
        pass
