from typing import Any

import pika
import pydantic
from loguru import logger
from pika.adapters.blocking_connection import BlockingChannel

from shared.events.user import UserCreatedEvent

ROUTING_TABLE: dict[str, list[str]] = {
    "user_created": ["queue_order"],
    # Future: "user_deleted": ["audit_events"], etc.
}


# TODO: event: dict[str, Any]) -> replace by Pydantic event model
def forward_event(channel: BlockingChannel, raw_event: dict[str, Any]) -> None:
    """Validates and dispatches an event to one or more queues based on the routing table."""

    # Validate the structure and lock the event type
    try:
        event = UserCreatedEvent.model_validate(raw_event)
    except pydantic.ValidationError as e:
        logger.error(f"❌ Invalid event payload: {raw_event} | Error: {e}")
        return

    # Dispatch based on event type
    for queue in ROUTING_TABLE.get(event.event, []):
        channel.basic_publish(
            exchange="",
            routing_key=queue,
            body=event.model_dump_json(),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        logger.info(f" → Forwarded '{event.event}' to queue '{queue}'")

    if event.event not in ROUTING_TABLE:
        logger.warning(f" ⚠️ Unrouted event type: '{event.event}'")
