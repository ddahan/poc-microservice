from typing import Any

import pika

from shared.events.user import UserCreatedEvent

from .config import get_settings

settings = get_settings()
params = pika.URLParameters(settings.RABBITMQ_URL)

connection = pika.BlockingConnection(params)
channel: Any = connection.channel()


def publish_user_created(user_id: str, name: str, email: str) -> None:
    event = UserCreatedEvent(user_id=user_id, name=name, email=email)

    # Publish the event to the RabbitMQ
    channel.basic_publish(
        exchange="",
        routing_key="queue_dispatch",
        body=event.model_dump_json(),
        properties=pika.BasicProperties(delivery_mode=2),  # makes the message persistent
    )
