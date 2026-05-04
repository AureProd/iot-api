import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from iot_api.clients.mqtt import MQTTClient
from iot_api.clients.redis import RedisClient

logger = logging.getLogger(__name__)

class DeviceStrategy(ABC):
    @abstractmethod
    def get_config(self, device_id: str, device_name: str) -> Dict[str, Any]:
        """Retourne la configuration SYNC pour Google Smart Home."""
        pass

    @abstractmethod
    async def get_status(self, redis_client: RedisClient, device_id: str) -> Dict[str, Any]:
        """Retourne l'état actuel de l'appareil (QUERY)."""
        pass

    @abstractmethod
    async def execute_command(self, redis_client: RedisClient, mqtt_client: MQTTClient, device_id: str, status: bool) -> None:
        """Exécute une commande On/Off et lève une ValueError en cas de blocage."""
        pass