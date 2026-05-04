import logging

from fastapi import APIRouter, Depends
from collections import defaultdict

from iot_api.clients.mqtt import MQTTClient
from iot_api.clients.redis import RedisClient
from iot_api.core import config
from iot_api.dependencies.auth import get_connected_user
from iot_api.dependencies.mqtt import get_mqtt_client
from iot_api.dependencies.redis import get_redis_client
from iot_api.services.devices.registry import DeviceRegistry

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
    inputs = payload.get("inputs", [])
    
    if not inputs: 
        return {"requestId": request_id, "payload": {}}

    requested_action = inputs[0].get("intent")
    
    # --- SYNC intent: Used by Google to discover available devices ---
    if requested_action == "action.devices.SYNC":
        devices_config = []
        # Iterate directly over the DeviceConfig objects stored in the dictionary values
        for device in config.DEVICES.values():
            strategy = DeviceRegistry.get_strategy(device.type)
            # Clean property access using dot notation (device.id, device.name)
            devices_config.append(strategy.get_config(device.id, device.name))

        return {
            "requestId": request_id,
            "payload": {
                "agentUserId": user_id, 
                "devices": devices_config
            }
        }

    # --- QUERY intent: Used by Google to get the current state of devices ---
    if requested_action == "action.devices.QUERY":
        devices = inputs[0]["payload"]["devices"]
        device_states = {}

        for device in devices:
            device_id = device["id"]
            
            # Ultra-fast O(1) lookup using the device ID from our configuration dictionary
            device_info = config.DEVICES.get(device_id)
            
            if device_info:
                strategy = DeviceRegistry.get_strategy(device_info.type)
                device_states[device_id] = await strategy.get_status(redis_client, device_id)

        return {
            "requestId": request_id,
            "payload": {"devices": device_states}
        }

    # --- EXECUTE intent: Used by Google to send commands (e.g., Turn On/Off) ---
    if requested_action == "action.devices.EXECUTE":
        commands: list[dict] = inputs[0]["payload"]["commands"]
        success_ids = []
        failed_by_error = defaultdict(list)
        target_state = False

        for cmd in commands:
            for ex in cmd.get("execution", []):
                # Currently only handling OnOff commands
                if ex["command"] == "action.devices.commands.OnOff":
                    target_state = bool(ex["params"]["on"])
                    
                    for device in cmd.get("devices", []):
                        device_id = device["id"]
                        
                        # Retrieve device configuration to get its type
                        device_info = config.DEVICES.get(device_id)
                        
                        if device_info:
                            try:
                                strategy = DeviceRegistry.get_strategy(device_info.type)
                                await strategy.execute_command(redis_client, mqtt_client, device_id, target_state)
                                success_ids.append(device_id)
                            except ValueError as exc:
                                # Group failed devices by their specific error code (e.g., 'needsWater')
                                failed_by_error[str(exc)].append(device_id)

        # Build the response payload
        response_commands = []
        
        # Add successfully executed devices
        if success_ids:
            response_commands.append({
                "ids": success_ids,
                "status": "SUCCESS",
                "states": {"on": target_state, "online": True}
            })
            
        # Add devices that failed execution along with their error codes
        for exc_code, failed_ids in failed_by_error.items():
            response_commands.append({
                "ids": failed_ids,
                "status": "ERROR",
                "errorCode": exc_code
            })

        return {
            "requestId": request_id,
            "payload": {"commands": response_commands}
        }

    # Default fallback response for unsupported intents
    return {"requestId": request_id, "payload": {}}