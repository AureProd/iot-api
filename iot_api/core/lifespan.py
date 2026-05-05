import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from iot_api.clients.mqtt import MQTTClient
from iot_api.clients.redis import RedisClient
from iot_api.core import config
from iot_api.services.devices.registry import DeviceRegistry

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logger.info("Starting IOT API.")

    # Store client in state of FastAPI app
    app.state.redis = RedisClient()
    app.state.mqtt = MQTTClient()

    try:
        # Etablish all clients connections in same time
        await asyncio.gather(app.state.redis.connect(), app.state.mqtt.connect())

        # Dynamically setup MQTT subscriptions for all registered device types
        # We extract unique device types from our Pydantic config
        unique_device_types = set(device.type for device in config.DEVICES.values())

        for device_type in unique_device_types:
            strategy = DeviceRegistry.get_strategy(device_type)
            await strategy.setup_subscriptions(app.state.mqtt, app.state.redis)
            logger.info(f"Subscribed to MQTT topics for device type: {device_type}")

        yield
    except Exception as exc:
        logger.exception(f"Critical failure during startup: {exc}")
        raise

    logger.info("Shutdown IOT API.")

    # Close all clients connections in same time
    await asyncio.gather(app.state.redis.close(), app.state.mqtt.close(), return_exceptions=True)

    logger.info("IOT API shutdown complete.")
