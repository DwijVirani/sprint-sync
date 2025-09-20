from pydantic import BaseModel, Field
from typing import List

class ProfileResponse(BaseModel):
    """User profile response model."""

    id: int
    email: str = Field(..., description="The user's email address", example="user@example.com")
    first_name: str = Field(..., description="The user's first name", example="John")
    last_name: str = Field(..., description="The user's last name", example="Doe")
    avatar: str = Field(..., description="The URL of the user's avatar", example="http://example.com/avatar.jpg")
    isAdmin: bool = Field(..., description="Indicates if the user has admin privileges", example=False)

class UserResponse(BaseModel):
    """Response model for a single user."""

    id: int
    email: str = Field(..., description="The user's email address", example="user@example.com")
    first_name: str = Field(..., description="The user's first name", example="John")
    last_name: str = Field(..., description="The user's last name", example="Doe")
    avatar: str = Field(..., description="The URL of the user's avatar", example="http://example.com/avatar.jpg")

class UserListResponse(BaseModel):
    """Response model for a list of users."""

    users: List[UserResponse]