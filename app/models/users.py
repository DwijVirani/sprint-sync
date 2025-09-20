from pydantic import BaseModel, Field
from typing import Optional, List
from .workflow import OrganizationResponse, UserOrganizationResponse


class ProfileResponse(BaseModel):
    """User profile response model."""

    id: int
    email: str = Field(..., description="The user's email address", example="user@example.com")
    first_name: str = Field(..., description="The user's first name", example="John")
    last_name: str = Field(..., description="The user's last name", example="Doe")
    avatar: Optional[str] = Field(None, description="The URL of the user's avatar", example="http://example.com/avatar.jpg")
    isAdmin: bool = Field(..., description="Indicates if the user has admin privileges", example=False)
    current_organization_id: Optional[int] = Field(None, description="Currently selected organization ID", example=1)
    current_organization: Optional[OrganizationResponse] = Field(None, description="Currently selected organization details")
    organizations: Optional[List[UserOrganizationResponse]] = Field(None, description="All organizations the user belongs to")


class UserResponse(BaseModel):
    """Response model for a single user."""

    id: int
    email: str = Field(..., description="The user's email address", example="user@example.com")
    first_name: str = Field(..., description="The user's first name", example="John")
    last_name: str = Field(..., description="The user's last name", example="Doe")
    avatar: Optional[str] = Field(None, description="The URL of the user's avatar", example="http://example.com/avatar.jpg")
    current_organization_id: Optional[int] = Field(None, description="Currently selected organization ID", example=1)


class UserListResponse(BaseModel):
    """Response model for a list of users."""

    users: List[UserResponse]