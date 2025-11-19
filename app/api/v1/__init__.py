from fastapi import APIRouter

from app.api.v1 import tasks

router = APIRouter()
router.include_router(tasks.router, tags=["tasks"])
