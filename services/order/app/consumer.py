import json
from typing import Any

import pika
from app.config import get_settings
from app.db import SessionLocal
from app.models import UserSnapshot
from loguru import logger
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from .db import engine
from .models import Base

settings = get_settings()


# Ensure the snapshot table exists
Base.metadata.create_all(bind=engine)


params = pika.URLParameters(settings.RABBITMQ_URL)

connection: pika.BlockingConnection = pika.BlockingConnection(params)
channel: Any = connection.channel()

# Declare the queue this service will consume (create if not exists, durable)
channel.queue_declare(queue="order_events", durable=True)


def callback(
    ch: BlockingChannel, method: Basic.Deliver, _properties: BasicProperties, body: bytes
) -> None:
    data: dict[str, Any] = json.loads(body)
    if data.get("event") == "user_created":
        db = SessionLocal()
        try:
            user = UserSnapshot(
                user_id=data["user_id"], name=data["name"], email=data["email"]
            )
            db.merge(user)
            db.commit()
        finally:
            db.close()

        ch.basic_ack(delivery_tag=method.delivery_tag)


# Set up consumer on 'order_events' queue
channel.basic_consume(queue="order_events", on_message_callback=callback)

logger.info(" [*] Order consumer running. To exit press CTRL+C")
channel.start_consuming()
