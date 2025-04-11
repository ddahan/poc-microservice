import json
from typing import Any

import pika
from loguru import logger
from pika.adapters.blocking_connection import BlockingChannel

ROUTING_TABLE: dict[str, list[str]] = {
    "user_created": ["order_events"],
    # Future: "user_deleted": ["audit_events"], etc.
}


# TODO: event: dict[str, Any]) -> replace by Pydantic event model
def forward_event(channel: BlockingChannel, event: dict[str, Any]) -> None:
    event_type: str = event["event"]

    for queue in ROUTING_TABLE.get(event_type, []):
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=json.dumps(event),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        logger.info(f" → Forwarded {event_type} to {queue}")

    if event_type not in ROUTING_TABLE:
        logger.warning(f" ⚠️ Unrouted event type: {event_type}")
