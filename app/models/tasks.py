from typing import List, Optional

from pydantic import BaseModel, Field

from .workflow import TaskStatusResponse


class TaskBase(BaseModel):
    """Base model for task."""

    title: str = Field(..., description="The task title", example="Implement feature X")
    description: str = Field(
        ...,
        description="The task description",
        example="Details about implementing feature X",
    )
    priority: str = Field(..., description="The task priority", example="high")
    assigned_to: int = Field(
        ..., description="The ID of the user to whom the task is assigned", example=43
    )
    collaborators: List[int] = Field(
        default=[],
        description="List of user IDs who are collaborators on the task",
        example=[43, 44],
    )
    total_minutes: int = Field(
        default=0, description="Total minutes spent on the task", example=120
    )
    comments: List[str] = Field(
        default=[],
        description="List of comments on the task",
        example=["Looks good!", "Please fix the bugs."],
    )
    due_date: Optional[str] = Field(
        None, description="The due date of the task", example="2023-01-01"
    )


class TaskCreate(TaskBase):
    """Model for creating a new task."""

    organization_id: int = Field(..., description="The organization ID", example=1)
    created_by: int = Field(
        ..., description="The ID of the user who created the task", example=42
    )
    status_id: Optional[int] = Field(
        None, description="The initial status ID (if not provided, uses org default)"
    )


class TaskUpdate(BaseModel):
    """Model for updating a task."""

    title: Optional[str] = Field(
        None, description="The task title", example="Implement feature X"
    )
    description: Optional[str] = Field(
        None,
        description="The task description",
        example="Details about implementing feature X",
    )
    priority: Optional[str] = Field(
        None, description="The task priority", example="high"
    )
    assigned_to: Optional[int] = Field(
        None, description="The ID of the user to whom the task is assigned", example=43
    )
    collaborators: Optional[List[int]] = Field(
        None,
        description="List of user IDs who are collaborators on the task",
        example=[43, 44],
    )
    total_minutes: Optional[int] = Field(
        None, description="Total minutes spent on the task", example=120
    )
    comments: Optional[List[str]] = Field(
        None,
        description="List of comments on the task",
        example=["Looks good!", "Please fix the bugs."],
    )
    due_date: Optional[str] = Field(
        None, description="The due date of the task", example="2023-01-01"
    )


class TaskResponse(TaskBase):
    """Response model for a single task."""

    id: int = Field(..., description="The task ID", example=1)
    organization_id: int = Field(..., description="The organization ID", example=1)
    created_by: int = Field(
        ..., description="The ID of the user who created the task", example=42
    )
    status_id: int = Field(..., description="The current status ID", example=2)
    # Optional: Include the full status object for convenience
    status: Optional[TaskStatusResponse] = Field(
        None, description="The current status details"
    )


class TaskListResponse(BaseModel):
    """Response model for a list of tasks."""

    tasks: List[TaskResponse]


class TaskStatusUpdateRequest(BaseModel):
    """Request model for updating a task's status."""

    to_status_id: int = Field(..., description="The new status ID", example=2)
    notes: Optional[str] = Field(
        None,
        description="Optional notes about the status change",
        example="Moved to QA after code review",
    )


class StatusTransitionResponse(BaseModel):
    """Response model for a status transition."""

    task_id: int = Field(..., description="The ID of the task", example=1)
    from_status: Optional[str] = Field(
        None,
        description="The status the task is transitioning from",
        example="in_progress",
    )
    to_status: str = Field(
        ..., description="The status the task is transitioning to", example="completed"
    )
    transitioned_at: str = Field(
        ...,
        description="The timestamp when the status was changed",
        example="2023-01-01T00:00:00Z",
    )
