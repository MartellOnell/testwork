import pytest

from app.models.task import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate
from app.services.task_service import TaskService


@pytest.mark.asyncio
async def test_create_task(test_db):
    async with test_db() as db:
        task_data = TaskCreate(
            title="Test Task",
            description="Test Description",
            priority=TaskPriority.HIGH
        )

        task = await TaskService.create_task(db, task_data)

        assert task.id is not None
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.NEW


@pytest.mark.asyncio
async def test_get_task(test_db):
    async with test_db() as db:
        task_data = TaskCreate(title="Test Task", priority=TaskPriority.MEDIUM)
        created_task = await TaskService.create_task(db, task_data)

        task = await TaskService.get_task(db, created_task.id)

        assert task is not None
        assert task.id == created_task.id
        assert task.title == "Test Task"


@pytest.mark.asyncio
async def test_get_tasks_with_filters(test_db):
    async with test_db() as db:
        await TaskService.create_task(db, TaskCreate(title="Task 1", priority=TaskPriority.HIGH))
        await TaskService.create_task(db, TaskCreate(title="Task 2", priority=TaskPriority.LOW))
        await TaskService.create_task(db, TaskCreate(title="Task 3", priority=TaskPriority.HIGH))

        tasks, total = await TaskService.get_tasks(db)
        assert total == 3
        assert len(tasks) == 3

        tasks, total = await TaskService.get_tasks(db, priority=TaskPriority.HIGH)
        assert total == 2
        assert len(tasks) == 2


@pytest.mark.asyncio
async def test_cancel_task(test_db):
    async with test_db() as db:
        task_data = TaskCreate(title="Test Task")
        task = await TaskService.create_task(db, task_data)

        cancelled_task = await TaskService.cancel_task(db, task.id)

        assert cancelled_task is not None
        assert cancelled_task.status == TaskStatus.CANCELLED
        assert cancelled_task.completed_at is not None


@pytest.mark.asyncio
async def test_update_task_status(test_db):
    async with test_db() as db:
        task_data = TaskCreate(title="Test Task")
        task = await TaskService.create_task(db, task_data)

        updated_task = await TaskService.update_task_status(
            db, task.id, TaskStatus.IN_PROGRESS
        )

        assert updated_task.status == TaskStatus.IN_PROGRESS
        assert updated_task.started_at is not None

        updated_task = await TaskService.update_task_status(
            db, task.id, TaskStatus.COMPLETED, result="Success"
        )

        assert updated_task.status == TaskStatus.COMPLETED
        assert updated_task.completed_at is not None
        assert updated_task.result == "Success"
