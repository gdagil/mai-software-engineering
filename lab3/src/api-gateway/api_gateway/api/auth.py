from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta

from api_gateway.models.auth import Token, UserLogin, UserResponse
from api_gateway.services.auth_service import authenticate_user, create_access_token
from api_gateway.dependencies import get_current_user
from api_gateway.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """
    Login with username and password to get JWT token
    
    Example request:
    ```json
    {
        "username": "admin",
        "password": "secret"
    }
    ```
    
    Example response:
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    ```
    """
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Get current authenticated user information
    
    Requires Bearer token in Authorization header.
    
    Example response:
    ```json
    {
        "id": 1,
        "username": "admin",
        "is_admin": true
    }
    ```
    """
    return current_user 