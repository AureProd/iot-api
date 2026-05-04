import asyncio
import logging
import ssl
from typing import Awaitable, Callable
import aiomqtt
from iot_api.core import config

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self._client = None
        self._listen_task = None
        
        self._subscriptions: dict[str, Callable[[str], Awaitable[None]]] = {}

    async def connect(self):
        if self._client: return

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.load_verify_locations(config.MQTT_CA_CERT_PATH)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self._client = aiomqtt.Client(
            hostname=config.MQTT_HOST,
            port=config.MQTT_PORT,
            username=config.MQTT_USERNAME,
            password=config.MQTT_PASSWORD,
            tls_context=ssl_context
        )

        try:
            await self._client.__aenter__()
            logger.info("MQTT Broker connected")
                        
            self._listen_task = asyncio.create_task(self._listen())
        except Exception as exc:
            logger.error(f"MQTT Connection failed: {exc}")
            raise exc

    async def close(self):
        if not self._client: return
        
        if self._listen_task: self._listen_task.cancel()
            
        await self._client.__aexit__(None, None, None)
        logger.info("MQTT Broker disconnected")
        
    async def _listen(self):
        try:
            async for message in self._client.messages:
                try:
                    # On garde l'objet Topic complet fourni par aiomqtt pour utiliser sa méthode .matches()
                    aiomqtt_topic = message.topic 
                    topic_str = aiomqtt_topic.value
                    payload_str = message.payload.decode()
                    logger.info(f"MQTT Received: {topic_str} -> {payload_str}")
                    
                    # On cherche la fonction correspondante en gérant les wildcards (+)
                    handler_found = False
                    for sub_pattern, handle_func in self._subscriptions.items():
                        if aiomqtt_topic.matches(sub_pattern):
                            handler_found = True
                            await handle_func(payload_str)
                            # On break si on part du principe qu'un message = un seul handler
                            break 
                            
                    if not handler_found:
                        logger.warning(f"No handler found for topic: {topic_str}")

                except Exception as exc:
                    logger.error(f"Error handling received MQTT message: {exc}")
        except asyncio.CancelledError:
            pass 
        except Exception as exc:
            logger.error(f"MQTT listen loop crashed: {exc}")

    async def subscribe(self, topic: str, handle_func: Callable[[str], Awaitable[None]]):
        self._subscriptions[topic] = handle_func
        await self._client.subscribe(topic)
        logger.info(f"Subscribed to MQTT '{topic}' topic.")
    
    async def publish(self, topic: str, payload: str):
        try:
            await self._client.publish(topic, payload=payload, qos=1)
            logger.info(f"MQTT Publish: {topic} -> {payload}")
        except Exception as exc:
            logger.error(f"Failed to publish MQTT message: {exc}")
