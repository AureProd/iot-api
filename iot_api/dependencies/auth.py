from fastapi import HTTPException, Request

from iot_api.helpers.jwt import verify_jwt


async def get_connected_user(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401)
    
    token = auth_header.split(" ")[1]
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401)
    return str(payload["sub"])