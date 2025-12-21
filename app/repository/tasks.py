from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.entities import Task
from app.utils.config import Config

config = Config()


class TasksRepository:
    def __init__(self, session: Session):
        self.session: Session = session

    async def create_task(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_task(self, task_id: int) -> Optional[Task]:
        stmt = select(Task).where(Task.id == task_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_task(self, task: Task) -> Task:
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete_task(self, task: Task) -> None:
        await self.session.delete(task)
        await self.session.commit()

    async def list_tasks(self, skip: int = 0, limit: int = 100) -> list[Task]:
        stmt = select(Task).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
