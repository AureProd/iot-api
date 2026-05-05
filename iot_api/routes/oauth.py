from fastapi import APIRouter, Depends, Form
from fastapi.responses import RedirectResponse

from iot_api.services.oauth import OAuthService

router = APIRouter(prefix="/auth", tags=["OAUTH"])


@router.get("/authorize")
async def authorize(
    client_id: str,
    redirect_uri: str,
    state: str,
    response_type: str,
    oauth_service: OAuthService = Depends(OAuthService),
):
    """
    Handles the initial OAuth2 authorization request.
    Delegates validation and code generation to the OAuthService.
    """
    # Let the service handle the business logic
    oauth_code = await oauth_service.process_authorization_request(client_id)

    # Return the HTTP redirect
    return RedirectResponse(url=f"{redirect_uri}?code={oauth_code}&state={state}")


@router.post("/token")
async def token_exchange(
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    code: str = Form(None),
    refresh_token: str = Form(None),
    oauth_service: OAuthService = Depends(OAuthService),
):
    """
    Handles the token exchange.
    Delegates all validations and token generation to the OAuthService.
    """
    # The service returns the exact dictionary payload needed for the response
    token_payload = await oauth_service.process_token_exchange(
        grant_type=grant_type,
        client_id=client_id,
        client_secret=client_secret,
        code=code,
        refresh_token=refresh_token,
    )

    return token_payload
