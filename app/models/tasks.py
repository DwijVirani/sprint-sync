from pydantic import BaseModel, Field, Optional


class TaskResponse(BaseModel):
    """Response model for a single task."""

    id: int = Field(..., description="The task ID", example=1)
    title: str = Field(..., description="The task title", example="Implement feature X")
    description: str = Field(
        ...,
        description="The task description",
        example="Details about implementing feature X",
    )
    status: str = Field(..., description="The task status", example="in_progress")
    priority: str = Field(..., description="The task priority", example="high")
    created_by: int = Field(
        ..., description="The ID of the user who created the task", example=42
    )
    collaborators: list[int] = Field(
        ...,
        description="List of user IDs who are collaborators on the task",
        example=[43, 44],
    )
    assigned_to: int = Field(
        ..., description="The ID of the user to whom the task is assigned", example=43
    )
    total_minutes: int = Field(
        ..., description="Total minutes spent on the task", example=120
    )
    comments: list[str] = Field(
        ...,
        description="List of comments on the task",
        example=["Looks good!", "Please fix the bugs."],
    )
    due_date: str = Field(
        ..., description="The due date of the task", example="2023-01-01"
    )


class TaskListResponse(BaseModel):
    """Response model for a list of tasks."""

    tasks: list[TaskResponse]


class StatusTransitionResponse(BaseModel):
    """Response model for a status transition."""

    task_id: int = Field(..., description="The ID of the task", example=1)
    from_status: str = Field(
        ...,
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


class CreateTaskRequest(BaseModel):
    """Request model for creating a new task."""

    title: str = Field(..., description="The task title", min_length=1)
    description: str = Field(..., description="The task description")
    status: str = Field(default="todo", description="The task status")
    priority: str = Field(default="medium", description="The task priority")
    assigned_to: int = Field(
        ..., description="The ID of the user to whom the task is assigned"
    )
    collaborators: list[int] = Field(
        default_factory=list, description="List of collaborator user IDs"
    )
    due_date: Optional[str] = Field(None, description="The due date of the task")


class UpdateTaskRequest(BaseModel):
    """Request model for updating a task."""

    title: Optional[str] = Field(None, description="The task title", min_length=1)
    description: Optional[str] = Field(None, description="The task description")
    status: Optional[str] = Field(None, description="The task status")
    priority: Optional[str] = Field(None, description="The task priority")
    assigned_to: Optional[int] = Field(
        None, description="The ID of the user to whom the task is assigned"
    )
    collaborators: Optional[list[int]] = Field(
        None, description="List of collaborator user IDs"
    )
    total_minutes: Optional[int] = Field(
        None, description="Total minutes spent on the task"
    )
    comments: Optional[list[str]] = Field(
        None, description="List of comments on the task"
    )
    due_date: Optional[str] = Field(None, description="The due date of the task")
