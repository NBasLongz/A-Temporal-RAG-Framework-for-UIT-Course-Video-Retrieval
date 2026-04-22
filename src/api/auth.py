from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas.user import Token
from src.services.user import UserService
from src.core.security import verify_password, create_access_token
from src.dependencies import get_user_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login/token", response_model=Token)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await user_service.get_user_by_email(email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token = create_access_token(subject=user.email)
    return Token(access_token=access_token, token_type="bearer")
