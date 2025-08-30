
from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    """Registration request model."""

    first_name: str = Field(..., description="The user's first name", example="John")
    last_name: str = Field(..., description="The user's last name", example="Doe")
    email: str = Field(..., description="The user's email address", example="user@example.com")
    password: str = Field(..., description="The user's password", example="password123")
    avatar: str = Field(..., description="The URL of the user's avatar", example="http://example.com/avatar.jpg")

class LoginRequest(BaseModel):
    """Login request model."""

    email: str = Field(..., description="The user's email address", example="user@example.com")
    password: str = Field(..., description="The user's password", example="password123")

class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str = Field(..., description="The access token", example="access_token")
    user: dict = Field(..., description="The user information", example={"id": 1, "email": "user@example.com"})
    token_type: str = Field(..., description="The type of the token", example="bearer")