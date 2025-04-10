import json
from typing import Any

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from .config import get_settings
from .db import SessionLocal, engine
from .models import Base, UserSnapshot

# Create the table if it doesn't exist yet
Base.metadata.create_all(bind=engine)

settings = get_settings()
params = pika.URLParameters(settings.RABBITMQ_URL)

connection: pika.BlockingConnection = pika.BlockingConnection(params)
channel: BlockingChannel = connection.channel()
channel.queue_declare(queue="user_created", durable=True)


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
            db.merge(user)  # insert or update
            db.commit()
        finally:
            db.close()

        ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(queue="user_created", on_message_callback=callback)

print(" [*] Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
