import os

APP_ENV = os.getenv("APP_ENV", "prod")
APP_URL = os.getenv("APP_URL", "https://jbhuet.fr")

ADMIN_EMAIL = "jbhuet0@gmail.com"

OAUTH_REDIRECT_URI = f"{APP_URL}/api/iot/auth/authorize"
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

JWT_PRIVATE_KEY_PATH="/app/certs/private.pem"
JWT_PUBLIC_KEY_PATH="/app/certs/public.pem"

MQTT_HOST = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

MQTT_CA_CERT_PATH="/mqtt/certs/ca.crt"

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

DEVICES = [
    ("led-01", "PC LED", "led"),
    # ("led-02", "BOOK LED", "led"),
    ("led-03", "COOK LED", "led"), 
    ("coffee-maker-01", "COFFEE MAKER", "coffee-maker"),  
]