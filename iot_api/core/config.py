import os

from iot_api.schemas.devices import DeviceConfig

APP_ENV = os.getenv("APP_ENV", "prod")

APP_SCHEME = os.getenv("APP_SCHEME", "https")
APP_HOST = os.getenv("APP_HOST", "jbhuet.fr")
APP_PORT = os.getenv("APP_PORT", "443")

APP_URL = f"{APP_SCHEME}://{APP_HOST}:{APP_PORT}"

ADMIN_EMAIL = "jbhuet0@gmail.com"

OAUTH_REDIRECT_URI = f"{APP_URL}/api/iot/auth/authorize"
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

JWT_PRIVATE_KEY_PATH = "/certs/api/private.pem"
JWT_PUBLIC_KEY_PATH = "/certs/api/public.pem"

MQTT_HOST = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))

MQTT_USERNAME = os.getenv("IOT_API_USERNAME")
MQTT_PASSWORD = os.getenv("IOT_API_PASSWORD")

MQTT_CA_CERT_PATH = "/certs/mqtt/ca.crt"

MQTT_LED_COMMAND_TOPIC = "home/led/{}/set"
MQTT_LED_STATUS_TOPIC = "home/led/{}/status"

MQTT_COFFEE_MAKER_COMMAND_TOPIC = "home/coffee/{}/set"
MQTT_COFFEE_MAKER_RUN_STATUS_TOPIC = "home/coffee/{}/run/status"
MQTT_COFFEE_MAKER_READY_STATUS_TOPIC = "home/coffee/{}/ready/status"

REDIS_OAUTH_CODE_TOPIC = "oauth:code:{}"
REDIS_OAUTH_REFRESH_TOPIC = "oauth:refresh:{}"

REDIS_LED_STATUS_TOPIC = "led:status:{}"
REDIS_COFFEE_MAKER_RUN_STATUS_TOPIC = "coffee:run:status:{}"
REDIS_COFFEE_MAKER_READY_STATUS_TOPIC = "coffee:ready:status:{}"

# DeviceConfig(id="led-02", name="BOOK LED", type="led"),
DEVICES_LIST: list[DeviceConfig] = [
    DeviceConfig(id="led-01", name="PC LED", type="led"),
    DeviceConfig(id="led-03", name="COOK LED", type="led"),
    DeviceConfig(id="coffee-maker-01", name="COFFEE MAKER", type="coffee-maker"),
    DeviceConfig(id="coffee-maker-status-01", name="COFFEE MAKER READY", type="coffee-maker-ready-sensor"),
]

# Dictionary comprehension to create a fast-lookup dictionary (O(1) access time) keyed by device ID.
# Pydantic models expect keyword arguments (id=..., name=..., type=...) for instantiation.
DEVICES: dict[str, DeviceConfig] = {device.id: device for device in DEVICES_LIST}
