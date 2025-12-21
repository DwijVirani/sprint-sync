"""
Task routes for SprintSync API

These routes provide CRUD operations for task management.
"""

import traceback

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.controller.tasks import TasksController
from app.db.session import get_session
from app.middleware.authorization import get_current_user
from app.models.tasks import (CreateTaskRequest, TaskListResponse,
                              TaskResponse, UpdateTaskRequest)

router = APIRouter(tags=["tasks"], prefix="/tasks")


def get_controller(session: Session = Depends(get_session)):
    return TasksController(session=session)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: CreateTaskRequest,
    controller: TasksController = Depends(get_controller),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new task

    Creates a new task with the provided details. The creating user is automatically
    set as the creator of the task.
    """
    try:
        task_data = request.model_dump()
        task_data["created_by"] = int(current_user["user_id"])
        task_data["total_minutes"] = 0
        task_data["comments"] = []

        task = await controller.create_task(task_data)

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            created_by=task.created_by,
            collaborators=(
                task.collaborators if isinstance(task.collaborators, list) else []
            ),
            assigned_to=task.assigned_to,
            total_minutes=task.total_minutes,
            comments=task.comments if isinstance(task.comments, list) else [],
            due_date=task.due_date or "",
        )
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    controller: TasksController = Depends(get_controller),
    current_user: dict = Depends(get_current_user),
):
    """
    Get a task by ID

    Retrieves the details of a specific task.
    """
    try:
        task = await controller.get_task(task_id)

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            created_by=task.created_by,
            collaborators=(
                task.collaborators if isinstance(task.collaborators, list) else []
            ),
            assigned_to=task.assigned_to,
            total_minutes=task.total_minutes,
            comments=task.comments if isinstance(task.comments, list) else [],
            due_date=task.due_date or "",
        )
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    request: UpdateTaskRequest,
    controller: TasksController = Depends(get_controller),
    current_user: dict = Depends(get_current_user),
):
    """
    Update a task

    Updates the specified task with the provided fields. Only provided fields
    will be updated.
    """
    try:
        # Only include fields that were actually provided in the request
        task_data = request.model_dump(exclude_unset=True)

        if not task_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update",
            )

        task = await controller.update_task(task_id, task_data)

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            created_by=task.created_by,
            collaborators=(
                task.collaborators if isinstance(task.collaborators, list) else []
            ),
            assigned_to=task.assigned_to,
            total_minutes=task.total_minutes,
            comments=task.comments if isinstance(task.comments, list) else [],
            due_date=task.due_date or "",
        )
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    controller: TasksController = Depends(get_controller),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a task

    Permanently deletes the specified task.
    """
    try:
        await controller.delete_task(task_id)
        return None
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    controller: TasksController = Depends(get_controller),
    current_user: dict = Depends(get_current_user),
):
    """
    List tasks

    Retrieves a paginated list of tasks.

    - **skip**: Number of tasks to skip (for pagination)
    - **limit**: Maximum number of tasks to return
    """
    try:
        tasks = await controller.list_tasks(skip=skip, limit=limit)

        task_responses = [
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                created_by=task.created_by,
                collaborators=(
                    task.collaborators if isinstance(task.collaborators, list) else []
                ),
                assigned_to=task.assigned_to,
                total_minutes=task.total_minutes,
                comments=task.comments if isinstance(task.comments, list) else [],
                due_date=task.due_date or "",
            )
            for task in tasks
        ]

        return TaskListResponse(tasks=task_responses)
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
