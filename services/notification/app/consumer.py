import json
from typing import Any

import pika
from app.config import get_settings
from app.dispatcher import forward_event
from loguru import logger
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

settings = get_settings()
params = pika.URLParameters(settings.RABBITMQ_URL)

connection: pika.BlockingConnection = pika.BlockingConnection(params)
channel: Any = connection.channel()

# Listen to notification dispatch queue
channel.queue_declare(queue="notification_dispatch", durable=True)


def callback(
    ch: BlockingChannel, method: Basic.Deliver, _properties: BasicProperties, body: bytes
) -> None:
    data: dict[str, Any] = json.loads(body)
    forward_event(channel, data)
    ch.basic_ack(delivery_tag=method.delivery_tag)


# Set up consumer: link queue to callback function
channel.basic_consume(queue="notification_dispatch", on_message_callback=callback)

# Start consuming messages (blocking loop)
logger.info(" [*] Notification dispatcher running. To exit press CTRL+C")
channel.start_consuming()
