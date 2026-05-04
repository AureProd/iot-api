from typing import Literal

from iot_api.clients.mqtt import MQTTClient
from iot_api.clients.redis import RedisClient
from iot_api.services.command import publish_coffee_maker_command, publish_led_command
from iot_api.services.status import get_coffee_maker_ready_status, get_coffee_maker_run_status, get_led_status


def get_device_config(
    device_id: str,
    device_name: str, 
    device_type: Literal["led", "coffee-maker"]    
) -> dict:
    match device_type:
        case "led":
            return {
                "id": device_id,
                "name": {"name": device_name},
                "type": "action.devices.types.LIGHT",
                "traits": ["action.devices.traits.OnOff"],
                "willReportState": True
            }
        case "coffee-maker":
            return {
                "id": device_id,
                "name": {"name": device_name},
                "type": "action.devices.types.COFFEE_MAKER",
                "traits": [
                    "action.devices.traits.OnOff", 
                    "action.devices.traits.StatusReport"
                ],
                "attributes": {
                    "pausable": False
                },
                "willReportState": True
            }
            
    raise NotImplementedError(f"Device type '{device_type}' not implemented.")
            
async def get_device_status(
    redis_client: RedisClient,
    device_id: str,
    device_type: Literal["led", "coffee-maker"]   
) -> dict:
    try:
        match device_type:
            case "led":
                return {
                    "on": await get_led_status(redis_client, device_id),
                    "online": True
                }
            case "coffee-maker":
                is_started = await get_coffee_maker_run_status(redis_client, device_id)
                is_ready = await get_coffee_maker_ready_status(redis_client, device_id)
                
                status_report = []
                # If coffee-maker is not ready no water or coffee
                if not is_ready:
                    status_report.append({
                        "blocking": True,
                        "priority": 0,
                        "statusCode": "needsWater" # Explicit to google coffee maker need water
                    })

                return {
                    "on": is_started,
                    "online": True,
                    "currentStatusReport": status_report
                }
    
    except TimeoutError:
        return {
            "on": False,
            "online": False
        }
            
    raise NotImplementedError(f"Device type '{device_type}' not implemented.")

async def publish_device_command(
    redis_client: RedisClient,
    mqtt_client: MQTTClient, 
    device_id: str, 
    device_type: Literal["led", "coffee-maker"], 
    status: bool
):    
    match device_type:
        case "led":
            await publish_led_command(mqtt_client, device_id, status)
        case "coffee-maker":
            is_started = await get_coffee_maker_run_status(redis_client, device_id)
            
            if status and not is_started:
                is_ready = await get_coffee_maker_ready_status(redis_client, device_id)
                
                if is_ready:
                    await publish_coffee_maker_command(mqtt_client, device_id, status)
                else:
                    raise ValueError("needsWater")
            elif not status and is_started:
                await publish_coffee_maker_command(mqtt_client, device_id, status)           
        case _:
            raise NotImplementedError(f"Device type '{device_type}' not implemented.")