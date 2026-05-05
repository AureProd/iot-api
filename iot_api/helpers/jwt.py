from datetime import datetime, timedelta, timezone
from functools import lru_cache

import jwt

from iot_api.core import config


@lru_cache(maxsize=1)
def get_private_key() -> str:
    """Reads and caches the private RSA key in memory to avoid repetitive disk I/O."""
    with open(config.JWT_PRIVATE_KEY_PATH, "r") as f:
        return f.read()


@lru_cache(maxsize=1)
def get_public_key() -> str:
    """Reads and caches the public RSA key in memory."""
    with open(config.JWT_PUBLIC_KEY_PATH, "r") as f:
        return f.read()


def generate_jwt(user_email: str, expires_delta: int = 3600) -> str:
    """Generates an RS256 encoded JWT token with a specific expiration time."""
    payload = {
        "sub": user_email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_delta),
        "iss": "iot-auth",
    }
    # Retrieve the cached key instead of opening the file
    return jwt.encode(payload, get_private_key(), algorithm="RS256")


def verify_jwt(token: str):
    """Verifies the JWT token and returns the payload if valid, None otherwise."""
    try:
        # Retrieve the cached key instead of opening the file
        return jwt.decode(token, get_public_key(), algorithms=["RS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
