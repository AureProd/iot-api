from iot_api.services.devices.base import DeviceStrategy
from iot_api.services.devices.led import LedStrategy
from iot_api.services.devices.coffee_maker import CoffeeMakerStrategy

class DeviceRegistry:
    _strategies: dict[str, DeviceStrategy] = {
        "led": LedStrategy(),
        "coffee-maker": CoffeeMakerStrategy()
    }

    @classmethod
    def get_strategy(cls, device_type: str) -> DeviceStrategy:
        strategy = cls._strategies.get(device_type)
        if not strategy:
            raise NotImplementedError(f"Device type '{device_type}' not implemented.")
        return strategy