import logging

from fastapi import APIRouter, Depends

from iot_api.clients.mqtt import MQTTClient
from iot_api.clients.redis import RedisClient
from iot_api.core import config
from iot_api.dependencies.auth import get_connected_user
from iot_api.dependencies.mqtt import get_mqtt_client
from iot_api.dependencies.redis import get_redis_client
from iot_api.helpers.devices import get_device_config, get_device_status, publish_device_command
from iot_api.services.command import publish_led_command
from iot_api.services.status import get_coffee_maker_ready_status, get_led_status

router = APIRouter(tags=["IOT"])

logger = logging.getLogger(__name__)

@router.post("/handler")
async def smart_home_handler(
    payload: dict, 
    redis_client: RedisClient = Depends(get_redis_client),
    mqtt_client: MQTTClient = Depends(get_mqtt_client),
    user_id: str = Depends(get_connected_user),
):
    request_id = payload.get("requestId")
    inputs: list[dict] = payload.get("inputs", [])
    
    if not inputs: 
        return {"requestId": request_id, "payload": {}}

    requested_action = inputs[0].get("intent")

    # --- SYNC action ---
    if requested_action == "action.devices.SYNC":
        return {
            "requestId": request_id,
            "payload": {
                "agentUserId": user_id,
                "devices": [
                    get_device_config(device_id, device_name, device_type)
                    for device_id, device_name, device_type in config.DEVICES
                ]
            }
        }

    # --- QUERY current device status ---
    if requested_action == "action.devices.QUERY":
        devices = inputs[0]["payload"]["devices"]
        device_states = {}
        
        devices_by_ids = {
            device_id: device_type
            for device_id, _, device_type in config.DEVICES
        }

        for device in devices:
            device_id = device["id"]
            device_states[device_id] = await get_device_status(redis_client, device_id, devices_by_ids[device_id])

        return {
            "requestId": request_id,
            "payload": {
                "devices": device_states
            }
        }

    # --- EXECUTE on/off command to change device status ---
    if requested_action == "action.devices.EXECUTE":
        commands: list[dict] = inputs[0]["payload"]["commands"]
        target_state = False
        
        devices_by_ids = {
            device_id: device_type
            for device_id, _, device_type in config.DEVICES
        }
        
        success_devices_ids: list[str] = []
        failed_devices_ids_by_exception: dict[str, list[str]] = {}
        for cmd in commands:
            devices = cmd.get("devices", [])
            
            for ex in cmd.get("execution", []):
                if ex["command"] == "action.devices.commands.OnOff":
                    target_state = bool(ex["params"]["on"])
                    
                    for device in devices:
                        device_id = device["id"]
                        
                        try:
                            await publish_device_command(
                                redis_client,
                                mqtt_client,
                                device_id,
                                devices_by_ids[device_id],
                                target_state
                            )                       
                            success_devices_ids.append(device_id)
                        except ValueError as exc:
                            failed_devices_ids = failed_devices_ids_by_exception.get(str(exc))
                            if failed_devices_ids is None:
                                failed_devices_ids_by_exception[str(exc)] = [device_id]
                            else:
                                failed_devices_ids.append(device_id)
                 
        response_commands = [
            {
                "ids": success_devices_ids,
                "status": "SUCCESS",
                "states": {"on": target_state, "online": True}
            }
        ]
        response_commands.extend((
            {
                "ids": devices_ids,
                "status": "ERROR",
                "errorCode": exc_code
            }
            for exc_code, devices_ids in failed_devices_ids_by_exception.items()
        ))
                            
        return {
            "requestId": request_id,
            "payload": {
                "commands": response_commands
            }
        }

    return {"requestId": request_id, "payload": {}}