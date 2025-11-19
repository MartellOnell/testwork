from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[str]
    error_message: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class TaskStatusResponse(BaseModel):
    id: int
    status: TaskStatus

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    tasks: list[TaskResponse]
