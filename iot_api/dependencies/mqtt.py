

from fastapi import Request

from iot_api.clients.mqtt import MQTTClient


def get_mqtt_client(request: Request) -> MQTTClient:
    return request.app.state.mqtt