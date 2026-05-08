import logging
from collections import defaultdict
from typing import Any

from fastapi import APIRouter, Depends

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
        devices_config: list[dict[str, Any]] = []
        # Iterate directly over the DeviceConfig objects stored in the dictionary values
        for device in config.DEVICES.values():
            strategy = DeviceRegistry.get_strategy(device.type)
            # Clean property access using dot notation (device.id, device.name)
            devices_config.append(strategy.get_config(device.id, device.name))

        return {"requestId": request_id, "payload": {"agentUserId": user_id, "devices": devices_config}}

    # --- QUERY intent: Used by Google to get the current state of devices ---
    if requested_action == "action.devices.QUERY":
        payload_devices: list[dict] = inputs[0]["payload"]["devices"]
        device_states: dict[str, dict[str, Any]] = {}

        for payload_device in payload_devices:
            device_id = str(payload_device["id"])

            # Ultra-fast O(1) lookup using the device ID from our configuration dictionary
            device_info = config.DEVICES.get(device_id)

            if device_info:
                strategy = DeviceRegistry.get_strategy(device_info.type)
                device_states[device_id] = await strategy.get_status(redis_client, device_id)

        return {"requestId": request_id, "payload": {"devices": device_states}}

    # --- EXECUTE intent: Used by Google to send commands (e.g., Turn On/Off) ---
    if requested_action == "action.devices.EXECUTE":
        commands: list[dict] = inputs[0]["payload"]["commands"]
        success_ids: list[str] = []
        failed_ids_by_exc: dict[str, list[str]] = defaultdict(list)
        target_state = False

        for cmd in commands:
            for ex in cmd.get("execution", []):
                # Currently only handling OnOff commands
                if ex["command"] == "action.devices.commands.OnOff":
                    target_state = bool(ex["params"]["on"])

                    for payload_device in cmd.get("devices", []):
                        device_id = str(payload_device["id"])

                        # Retrieve device configuration to get its type
                        device_info = config.DEVICES.get(device_id)

                        if device_info:
                            try:
                                strategy = DeviceRegistry.get_strategy(device_info.type)
                                await strategy.execute_command(redis_client, mqtt_client, device_id, target_state)
                                success_ids.append(device_id)
                            except ValueError as exc:
                                logger.warning(f"An error has occured with device command: '{str(exc)}'")
                                # Group failed devices by their specific error code (e.g., 'needsWater')
                                failed_ids_by_exc[str(exc)].append(device_id)

        # Build the response payload
        response_commands = []

        # Add successfully executed devices
        if success_ids:
            response_commands.append(
                {"ids": success_ids, "status": "SUCCESS", "states": {"on": target_state, "online": True}}
            )

        # Add devices that failed execution along with their error codes
        for exc_code, failed_ids in failed_ids_by_exc.items():
            response_commands.append(
                {
                    "ids": failed_ids,
                    "status": "ERROR",
                    "errorCode": exc_code,
                }
            )

        return {"requestId": request_id, "payload": {"commands": response_commands}}

    # Default fallback response for unsupported intents
    return {"requestId": request_id, "payload": {}}
