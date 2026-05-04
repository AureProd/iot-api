import jwt
from datetime import datetime, timedelta, timezone
from iot_api.core import config

def generate_jwt(user_email: str, expires_delta: int = 3600) -> str:
    with open(config.JWT_PRIVATE_KEY_PATH, "r") as f:
        priv_key = f.read()
    
    payload = {
        "sub": user_email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_delta),
        "iss": "iot-auth"
    }
    return jwt.encode(payload, priv_key, algorithm="RS256")

def verify_jwt(token: str):
    with open(config.JWT_PUBLIC_KEY_PATH, "r") as f:
        pub_key = f.read()
    try:
        return jwt.decode(token, pub_key, algorithms=["RS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None