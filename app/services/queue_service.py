import json
import logging
from typing import Optional

import aio_pika
from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractChannel, AbstractConnection

from app.core.config import settings

logger = logging.getLogger(__name__)


class QueueService:
    def __init__(self):
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.queue: Optional[aio_pika.Queue] = None

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=settings.MAX_CONCURRENT_TASKS)

            self.queue = await self.channel.declare_queue(
                settings.RABBITMQ_QUEUE,
                durable=True
            )
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self):
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")

    async def publish_task(self, task_id: int, priority: int = 0):
        if not self.channel:
            raise RuntimeError("Not connected to RabbitMQ")

        message_body = json.dumps({"task_id": task_id})
        message = Message(
            body=message_body.encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            priority=priority
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key=settings.RABBITMQ_QUEUE
        )
        logger.info(f"Published task {task_id} to queue")

    async def consume_tasks(self, callback):
        if not self.queue:
            raise RuntimeError("Queue not initialized")

        await self.queue.consume(callback)
        logger.info("Started consuming tasks")


queue_service = QueueService()