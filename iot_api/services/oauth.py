import uuid
from fastapi import Depends, HTTPException

from iot_api.clients.redis import RedisClient
from iot_api.core import config
from iot_api.dependencies.redis import get_redis_client
from iot_api.helpers.jwt import generate_jwt


class OAuthService:
    """
    Handles all business logic related to OAuth2 authentication flows,
    including authorization code generation and token exchange.
    """
    def __init__(self, redis_client: RedisClient = Depends(get_redis_client)):
        self.redis_client = redis_client

    async def process_authorization_request(self, client_id: str) -> str:
        """
        Validates the client ID and generates a temporary authorization code.
        """
        if client_id != config.OAUTH_CLIENT_ID:
            raise HTTPException(status_code=400, detail="Invalid Client ID")
        
        # Generate a secure random code
        oauth_code = str(uuid.uuid4())
        
        # Save to Redis with a 10-minute TTL
        topic = config.REDIS_OAUTH_CODE_TOPIC.format(oauth_code)
        await self.redis_client.set(topic, config.ADMIN_EMAIL, 600)
        
        return oauth_code

    async def process_token_exchange(
        self,
        grant_type: str,
        client_id: str,
        client_secret: str,
        code: str | None,
        refresh_token: str | None
    ) -> dict:
        """
        Validates credentials and exchanges a code or refresh token for a new JWT pair.
        """
        # 1. Validate Client Credentials
        if client_id != config.OAUTH_CLIENT_ID or client_secret != config.OAUTH_CLIENT_SECRET:
            raise HTTPException(status_code=401, detail="Invalid Client Credentials")

        user_email = None

        # 2. Process Grant Type
        if grant_type == "authorization_code":
            if not code:
                raise HTTPException(status_code=400, detail="Missing authorization code")
            user_email = await self._get_user_by_auth_code(code)
                
        elif grant_type == "refresh_token":
            if not refresh_token:
                raise HTTPException(status_code=400, detail="Missing refresh token")
            user_email = await self._get_user_by_refresh_token(refresh_token)
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported grant type")
        
        # 3. Validate User
        if user_email != config.ADMIN_EMAIL:
            raise HTTPException(status_code=401, detail="Unauthorized user")

        # 4. Generate New Tokens
        token_expiration_seconds = 3600
        new_access_token = generate_jwt(user_email, token_expiration_seconds)
        new_refresh_token = str(uuid.uuid4())
        
        # Save new refresh token to Redis
        refresh_topic = config.REDIS_OAUTH_REFRESH_TOPIC.format(new_refresh_token)
        await self.redis_client.set(refresh_topic, user_email, 2592000) # 30 days TTL

        return {
            "token_type": "Bearer",
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "expires_in": token_expiration_seconds
        }

    # --- Private Helper Methods for Redis Interactions ---

    async def _get_user_by_auth_code(self, code: str) -> str:
        """Retrieves user by auth code and deletes it (one-time use)."""
        topic = config.REDIS_OAUTH_CODE_TOPIC.format(code)
        user_email = await self.redis_client.pop(topic)
        if not user_email:
            raise HTTPException(status_code=400, detail="Invalid or expired authorization code")
        return user_email

    async def _get_user_by_refresh_token(self, token: str) -> str:
        """Retrieves user by refresh token."""
        topic = config.REDIS_OAUTH_REFRESH_TOPIC.format(token)
        user_email = await self.redis_client.get(topic)
        if not user_email:
            raise HTTPException(status_code=400, detail="Invalid or expired refresh token")
        return user_email