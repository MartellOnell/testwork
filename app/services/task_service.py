from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    @staticmethod
    async def create_task(db: AsyncSession, task_data: TaskCreate) -> Task:
        task = Task(
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            status=TaskStatus.NEW
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def get_task(db: AsyncSession, task_id: int) -> Optional[Task]:
        result = await db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tasks(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
    ) -> tuple[List[Task], int]:
        query = select(Task)
        count_query = select(func.count(Task.id))

        filters = []
        if status:
            filters.append(Task.status == status)
        if priority:
            filters.append(Task.priority == priority)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        query = query.order_by(Task.created_at.desc())

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        tasks = list(result.scalars().all())

        count_result = await db.execute(count_query)
        total = count_result.scalar()

        return tasks, total

    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: int,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        task = await TaskService.get_task(db, task_id)
        if not task:
            return None

        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def cancel_task(db: AsyncSession, task_id: int) -> Optional[Task]:
        task = await TaskService.get_task(db, task_id)
        if not task:
            return None

        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return None

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def update_task_status(
        db: AsyncSession,
        task_id: int,
        status: TaskStatus,
        result: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[Task]:
        task = await TaskService.get_task(db, task_id)
        if not task:
            return None

        task.status = status

        if status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.utcnow()

        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            task.completed_at = datetime.utcnow()

        if result:
            task.result = result

        if error_message:
            task.error_message = error_message

        await db.commit()
        await db.refresh(task)
        return task
