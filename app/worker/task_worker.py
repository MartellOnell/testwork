import asyncio
import json
import logging
from datetime import datetime

from aio_pika.abc import AbstractIncomingMessage

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.task import TaskStatus
from app.services.queue_service import queue_service
from app.services.task_service import TaskService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_task(task_id: int):
    async with AsyncSessionLocal() as db:
        await TaskService.update_task_status(
            db,
            task_id,
            TaskStatus.IN_PROGRESS
        )

        try:
            logger.info(f"Processing task {task_id}")
            await asyncio.sleep(settings.TASK_PROCESSING_DELAY)

            result = f"Task {task_id} completed successfully at {datetime.utcnow()}"
            await TaskService.update_task_status(
                db,
                task_id,
                TaskStatus.COMPLETED,
                result=result
            )
            logger.info(f"Task {task_id} completed")

        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            await TaskService.update_task_status(
                db,
                task_id,
                TaskStatus.FAILED,
                error_message=str(e)
            )


async def on_message(message: AbstractIncomingMessage):
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            task_id = data.get("task_id")

            if not task_id:
                logger.error("No task_id in message")
                return

            await process_task(task_id)

        except Exception as e:
            logger.error(f"Error processing message: {e}")


async def main():
    logger.info("Starting task worker...")

    await queue_service.connect()

    await queue_service.consume_tasks(on_message)

    logger.info("Worker is running. Press Ctrl+C to stop.")

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        logger.info("Shutting down worker...")
    finally:
        await queue_service.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
