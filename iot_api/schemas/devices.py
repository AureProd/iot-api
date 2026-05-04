from typing import Literal

from pydantic import BaseModel


class DeviceConfig(BaseModel):
    """
    Pydantic model representing a smart home device configuration.
    Enforces strict type validation on initialization to prevent bugs.
    """
    id: str
    name: str
    type: Literal["led", "coffee-maker"] # Strict validation for allowed device types