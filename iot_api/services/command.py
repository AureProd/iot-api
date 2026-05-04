import json

from iot_api.clients.mqtt import MQTTClient
from iot_api.core import config


async def publish_led_command(mqtt_client: MQTTClient, led_id: str, status: bool):
    topic = config.MQTT_LED_COMMAND_TOPIC.format(led_id)
    payload = {
        "id": led_id,
        "status": 1 if status else 0
    }
    await mqtt_client.publish(topic, json.dumps(payload))
    
async def publish_coffee_maker_command(mqtt_client: MQTTClient, coffee_maker_id: str, status: bool):
    topic = config.MQTT_COFFEE_MAKER_COMMAND_TOPIC.format(coffee_maker_id)
    payload = {
        "id": coffee_maker_id,
        "status": 1 if status else 0
    }
    await mqtt_client.publish(topic, json.dumps(payload))