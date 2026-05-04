from iot_api.services.devices.base import DeviceStrategy
from iot_api.services.devices.led import LedStrategy
from iot_api.services.devices.coffee_maker import CoffeeMakerStrategy

class DeviceRegistry:
    """
    Registry pattern to map device type strings to their respective strategy classes.
    To add a new device type, just instantiate its strategy here.
    """
    _strategies: dict[str, DeviceStrategy] = {
        "led": LedStrategy(),
        "coffee-maker": CoffeeMakerStrategy()
    }

    @classmethod
    def get_strategy(cls, device_type: str) -> DeviceStrategy:
        """Retrieves the strategy instance based on the device type."""
        strategy = cls._strategies.get(device_type)
        if not strategy:
            raise NotImplementedError(f"Device type '{device_type}' not implemented.")
        return strategy