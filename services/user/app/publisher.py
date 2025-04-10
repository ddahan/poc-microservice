import json

import pika

from .config import get_settings

settings = get_settings()
params = pika.URLParameters(settings.RABBITMQ_URL)

connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="user_created", durable=True)


def publish_user_created(user_id: str, name: str, email: str) -> None:
    event = {"event": "user_created", "user_id": user_id, "name": name, "email": email}

    # Publish the event to the RabbitMQ default exchange with the queue name as routing_key
    channel.basic_publish(
        exchange="",
        routing_key="user_created",
        body=json.dumps(event),
        properties=pika.BasicProperties(delivery_mode=2),  # makes the message persistent
    )
