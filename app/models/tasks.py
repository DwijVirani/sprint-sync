from pydantic import BaseModel, Field

class TaskResponse(BaseModel):
    """Response model for a single task."""

    id: int = Field(..., description="The task ID", example=1)
    title: str = Field(..., description="The task title", example="Implement feature X")
    description: str = Field(..., description="The task description", example="Details about implementing feature X")
    status: str = Field(..., description="The task status", example="in_progress")
    priority: str = Field(..., description="The task priority", example="high")
    created_by: int = Field(..., description="The ID of the user who created the task", example=42)
    collaborators: list[int] = Field(..., description="List of user IDs who are collaborators on the task", example=[43, 44])
    assigned_to: int = Field(..., description="The ID of the user to whom the task is assigned", example=43)
    total_minutes: int = Field(..., description="Total minutes spent on the task", example=120)
    comments: list[str] = Field(..., description="List of comments on the task", example=["Looks good!", "Please fix the bugs."])
    due_date: str = Field(..., description="The due date of the task", example="2023-01-01")

class TaskListResponse(BaseModel):
    """Response model for a list of tasks."""

    tasks: list[TaskResponse]

class StatusTransitionResponse(BaseModel):
    """Response model for a status transition."""

    task_id: int = Field(..., description="The ID of the task", example=1)
    from_status: str = Field(..., description="The status the task is transitioning from", example="in_progress")
    to_status: str = Field(..., description="The status the task is transitioning to", example="completed")
    transitioned_at: str = Field(..., description="The timestamp when the status was changed", example="2023-01-01T00:00:00Z")