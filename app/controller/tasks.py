from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.entities import Task
from app.repository.tasks import TasksRepository


class TasksController:
    def __init__(self, session: Session):
        self.session = session
        self.tasks_repository: TasksRepository = TasksRepository(session)

    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        """Create a new task"""
        task = Task(**task_data)
        return await self.tasks_repository.create_task(task)

    async def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        task = await self.tasks_repository.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        return task

    async def update_task(self, task_id: int, task_data: Dict[str, Any]) -> Task:
        """Update a task"""
        task = await self.tasks_repository.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        for key, value in task_data.items():
            setattr(task, key, value)
        return await self.tasks_repository.update_task(task)

    async def delete_task(self, task_id: int) -> None:
        """Delete a task"""
        task = await self.tasks_repository.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        await self.tasks_repository.delete_task(task)

    async def list_tasks(self, skip: int = 0, limit: int = 100) -> list[Task]:
        """List tasks"""
        return await self.tasks_repository.list_tasks(skip=skip, limit=limit)
