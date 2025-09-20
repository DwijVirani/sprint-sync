from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskStatusBase(BaseModel):
    """Base model for task status."""

    name: str = Field(
        ..., description="Internal name for the status", example="in_progress"
    )
    display_name: str = Field(
        ..., description="Display name for the status", example="In Progress"
    )
    color: Optional[str] = Field(
        None, description="Hex color code for UI display", example="#3B82F6"
    )
    order_index: int = Field(
        default=0, description="Order index for sorting statuses", example=2
    )
    is_active: bool = Field(default=True, description="Whether this status is active")
    is_default: bool = Field(
        default=False, description="Whether this is the default status for new tasks"
    )


class TaskStatusCreate(TaskStatusBase):
    """Model for creating a new task status."""

    organization_id: int = Field(
        ..., description="The organization ID this status belongs to", example=1
    )


class TaskStatusUpdate(BaseModel):
    """Model for updating a task status."""

    display_name: Optional[str] = Field(
        None, description="Display name for the status", example="In Progress"
    )
    color: Optional[str] = Field(
        None, description="Hex color code for UI display", example="#3B82F6"
    )
    order_index: Optional[int] = Field(
        None, description="Order index for sorting statuses", example=2
    )
    is_active: Optional[bool] = Field(None, description="Whether this status is active")
    is_default: Optional[bool] = Field(
        None, description="Whether this is the default status for new tasks"
    )


class TaskStatusResponse(TaskStatusBase):
    """Response model for a task status."""

    id: int = Field(..., description="The status ID", example=1)
    organization_id: int = Field(..., description="The organization ID", example=1)


class TaskWorkflowTransitionBase(BaseModel):
    """Base model for workflow transitions."""

    from_status_id: int = Field(..., description="The source status ID", example=1)
    to_status_id: int = Field(..., description="The target status ID", example=2)
    is_active: bool = Field(
        default=True, description="Whether this transition is active"
    )


class TaskWorkflowTransitionCreate(TaskWorkflowTransitionBase):
    """Model for creating a new workflow transition."""

    organization_id: int = Field(..., description="The organization ID", example=1)


class TaskWorkflowTransitionResponse(TaskWorkflowTransitionBase):
    """Response model for a workflow transition."""

    id: int = Field(..., description="The transition ID", example=1)
    organization_id: int = Field(..., description="The organization ID", example=1)


class TaskStatusTransitionBase(BaseModel):
    """Base model for task status transitions."""

    from_status_id: Optional[int] = Field(
        None, description="The previous status ID (null for initial status)", example=1
    )
    to_status_id: int = Field(..., description="The new status ID", example=2)
    notes: Optional[str] = Field(
        None,
        description="Optional notes about the transition",
        example="Moved to QA after code review",
    )


class TaskStatusTransitionCreate(TaskStatusTransitionBase):
    """Model for creating a new task status transition."""

    task_id: int = Field(..., description="The task ID", example=1)
    changed_by: int = Field(
        ..., description="The user ID who made the change", example=42
    )


class TaskStatusTransitionResponse(TaskStatusTransitionBase):
    """Response model for a task status transition."""

    id: int = Field(..., description="The transition ID", example=1)
    task_id: int = Field(..., description="The task ID", example=1)
    changed_by: int = Field(
        ..., description="The user ID who made the change", example=42
    )
    changed_at: datetime = Field(
        ..., description="When the transition occurred", example="2023-01-01T12:00:00Z"
    )


class OrganizationWorkflowResponse(BaseModel):
    """Response model for organization's complete workflow setup."""

    statuses: List[TaskStatusResponse] = Field(
        ..., description="All statuses for the organization"
    )
    transitions: List[TaskWorkflowTransitionResponse] = Field(
        ..., description="All allowed transitions"
    )


class WorkflowSetupRequest(BaseModel):
    """Request model for setting up a complete workflow for an organization."""

    statuses: List[TaskStatusCreate] = Field(
        ..., description="List of statuses to create"
    )
    transitions: List[TaskWorkflowTransitionCreate] = Field(
        ..., description="List of transitions to create"
    )


class OrganizationBase(BaseModel):
    """Base model for organization."""

    name: str = Field(..., description="Organization name", example="Acme Corp")
    description: Optional[str] = Field(
        None, description="Organization description", example="Leading software company"
    )


class OrganizationCreate(OrganizationBase):
    """Model for creating an organization."""

    pass


class OrganizationUpdate(BaseModel):
    """Model for updating an organization."""

    name: Optional[str] = Field(
        None, description="Organization name", example="Acme Corp"
    )
    description: Optional[str] = Field(
        None, description="Organization description", example="Leading software company"
    )


class OrganizationResponse(OrganizationBase):
    """Response model for an organization."""

    id: int = Field(..., description="The organization ID", example=1)


class UserOrganizationBase(BaseModel):
    """Base model for user-organization relationship."""

    role: str = Field(
        default="member", description="User's role in the organization", example="admin"
    )
    is_active: bool = Field(
        default=True, description="Whether the membership is active"
    )


class UserOrganizationCreate(UserOrganizationBase):
    """Model for creating a user-organization relationship."""

    user_id: int = Field(..., description="The user ID", example=42)
    organization_id: int = Field(..., description="The organization ID", example=1)


class UserOrganizationUpdate(BaseModel):
    """Model for updating a user-organization relationship."""

    role: Optional[str] = Field(
        None, description="User's role in the organization", example="admin"
    )
    is_active: Optional[bool] = Field(
        None, description="Whether the membership is active"
    )


class UserOrganizationResponse(UserOrganizationBase):
    """Response model for a user-organization relationship."""

    id: int = Field(..., description="The relationship ID", example=1)
    user_id: int = Field(..., description="The user ID", example=42)
    organization_id: int = Field(..., description="The organization ID", example=1)
    joined_at: datetime = Field(
        ...,
        description="When the user joined the organization",
        example="2023-01-01T12:00:00Z",
    )
    # Optional: Include organization details
    organization: Optional[OrganizationResponse] = Field(
        None, description="Organization details"
    )


class UserOrganizationsResponse(BaseModel):
    """Response model for all organizations a user belongs to."""

    organizations: List[UserOrganizationResponse] = Field(
        ..., description="List of user's organization memberships"
    )
    current_organization_id: Optional[int] = Field(
        None, description="Currently selected organization ID", example=1
    )


class SwitchOrganizationRequest(BaseModel):
    """Request model for switching user's current organization."""

    organization_id: int = Field(
        ..., description="The organization ID to switch to", example=1
    )


class SwitchOrganizationResponse(BaseModel):
    """Response model for organization switch."""

    success: bool = Field(
        ..., description="Whether the switch was successful", example=True
    )
    current_organization_id: int = Field(
        ..., description="The new current organization ID", example=1
    )
    organization: OrganizationResponse = Field(
        ..., description="Details of the current organization"
    )
