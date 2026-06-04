from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.auth_service import AuthService
from app.web.dependencies import get_auth_service
from app.web.schemas import LoginRequest, RefreshTokenRequest, TokenResponse

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    access_token, refresh_token = auth_service.login(request.username, request.password)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh_token(
    request: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    access_token, new_refresh_token = auth_service.refresh(request.refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/auth/logout", status_code=204)
def logout(
    request: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    auth_service.logout(request.refresh_token)
