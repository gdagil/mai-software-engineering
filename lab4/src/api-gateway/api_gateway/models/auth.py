from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class Token(BaseModel):
    access_token: str = Field(..., json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."})
    token_type: str = Field(..., json_schema_extra={"example": "bearer"})


class TokenData(BaseModel):
    username: Optional[str] = Field(None, json_schema_extra={"example": "admin"})


class UserLogin(BaseModel):
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Password for login")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "admin",
                "password": "secret"
            }
        }
    )


class UserResponse(BaseModel):
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    is_admin: bool = Field(..., description="Whether user has admin privileges")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "admin",
                "is_admin": True
            }
        }
    )


class User(BaseModel):
    id: int = Field(...)
    username: str = Field(...)
    password: str = Field(...)
    is_admin: bool = Field(False)


class UserInDB(User):
    hashed_password: str = Field(...) 