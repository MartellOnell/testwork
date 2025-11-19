from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.task import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskStatusResponse
from app.services.queue_service import queue_service
from app.services.task_service import TaskService

router = APIRouter()


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    task = await TaskService.create_task(db, task_data)

    await TaskService.update_task_status(db, task.id, TaskStatus.PENDING)

    priority_map = {
        TaskPriority.HIGH: 10,
        TaskPriority.MEDIUM: 5,
        TaskPriority.LOW: 1
    }
    await queue_service.publish_task(task.id, priority_map.get(task.priority, 5))

    await db.refresh(task)

    return task


@router.get("/tasks", response_model=TaskListResponse)
async def get_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    db: AsyncSession = Depends(get_db)
):
    skip = (page - 1) * page_size
    tasks, total = await TaskService.get_tasks(
        db,
        skip=skip,
        limit=page_size,
        status=status,
        priority=priority
    )

    return TaskListResponse(
        total=total,
        page=page,
        page_size=page_size,
        tasks=tasks
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    task = await TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}", response_model=TaskResponse)
async def cancel_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    task = await TaskService.cancel_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=400,
            detail="Task not found or cannot be cancelled"
        )
    return task


@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    task = await TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatusResponse(id=task.id, status=task.status)
