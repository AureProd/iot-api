import asyncio
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from iot_api.clients.mqtt import MQTTClient
from iot_api.clients.redis import RedisClient
from iot_api.core import config
from iot_api.services.status import handle_led_status, handle_coffee_maker_run_status, handle_coffee_maker_ready_status

logger = logging.getLogger(__name__)

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logger.info("Starting IOT API.")
    
    # Store client in state of FastAPI app
    app.state.redis = RedisClient()
    app.state.mqtt = MQTTClient()
    
    try:
        # Etablish all clients connections in same time
        await asyncio.gather(
            app.state.redis.connect(),
            app.state.mqtt.connect()
        )
        
        # Add MQTT topics subscribers
        await app.state.mqtt.subscribe(config.MQTT_LED_STATUS_TOPIC.format("+"), handle_led_status(app.state.redis))
        await app.state.mqtt.subscribe(config.MQTT_COFFEE_MAKER_RUN_STATUS_TOPIC.format("+"), handle_coffee_maker_run_status(app.state.redis))
        await app.state.mqtt.subscribe(config.MQTT_COFFEE_MAKER_READY_STATUS_TOPIC.format("+"), handle_coffee_maker_ready_status(app.state.redis))
        
        yield
    except Exception as exc:
        logger.exception(f"Critical failure during startup: {exc}")
        raise
    
    logger.info("Shutdown IOT API.")
    
    # Close all clients connections in same time
    await asyncio.gather(
        app.state.redis.close(),
        app.state.mqtt.close(),
        return_exceptions=True
    )
    
    logger.info("IOT API shutdown complete.")