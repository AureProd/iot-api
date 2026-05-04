from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from iot_api.clients.redis import RedisClient
import uuid

from iot_api.core import config
from iot_api.dependencies.redis import get_redis_client
from iot_api.helpers.jwt import generate_jwt
from iot_api.services.oauth import get_user_from_oauth_code, get_user_from_refresh_token, save_oauth_code, save_refresh_token

router = APIRouter(prefix="/auth", tags=["OAUTH"])

redis_manager = RedisClient()

@router.get("/authorize")
async def authorize(
    client_id: str, 
    redirect_uri: str, 
    state: str, 
    response_type: str,
    redis_client: RedisClient = Depends(get_redis_client),
):
    if client_id != config.OAUTH_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Invalid Client ID")
    
    oauth_code = str(uuid.uuid4())
    await save_oauth_code(redis_client, oauth_code, config.ADMIN_EMAIL) 
    
    return RedirectResponse(url=f"{redirect_uri}?code={oauth_code}&state={state}")

@router.post("/token")
async def token_exchange(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    code: str = Form(None),
    refresh_token: str = Form(None),
    redis_client: RedisClient = Depends(get_redis_client),
):
    if client_id != config.OAUTH_CLIENT_ID or client_secret != config.OAUTH_CLIENT_SECRET:
        raise HTTPException(status_code=401, detail="Invalid Client Credentials")

    user_email = None

    if grant_type == "authorization_code":
        user_email = await get_user_from_oauth_code(redis_client, code)
            
    elif grant_type == "refresh_token":
        user_email = await get_user_from_refresh_token(redis_client, refresh_token)
        
    else:
        raise HTTPException(status_code=400, detail="Unsupported grant type")
    
    if user_email != config.ADMIN_EMAIL:
        raise HTTPException(status_code=401)

    # Générer nouveaux tokens
    new_access_token = generate_jwt(user_email)
    new_refresh_token = str(uuid.uuid4())
    await save_refresh_token(redis_client, new_refresh_token, user_email)

    return {
        "token_type": "Bearer",
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "expires_in": 3600
    }