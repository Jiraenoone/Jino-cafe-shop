"""
messaging/publisher.py — Azure Service Bus Publisher

ส่ง OrderCreated message ไปยัง Service Bus queue
รองรับทั้ง Managed Identity (production) และ Connection String (development)
"""
import json
import logging
from datetime import datetime, timezone

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def publish_order_created(
    order_id: int,
    customer_name: str,
    customer_email: str,
    total_amount: float,
    items_count: int,
) -> bool:
    """
    ส่ง OrderCreated event ไปยัง Azure Service Bus

    Returns:
        True ถ้าส่งสำเร็จ, False ถ้าล้มเหลว (order ยังถูกบันทึกใน DB แล้ว)
    """
    if not settings.servicebus_queue_name:
        logger.warning("Service Bus not configured — skipping message publish")
        return False

    message_body = {
        "message_type": "OrderCreated",
        "order_id": order_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "total_amount": total_amount,
        "items_count": items_count,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        from azure.servicebus.aio import ServiceBusClient
        from azure.servicebus import ServiceBusMessage

        # เลือก authentication method
        if settings.use_managed_identity:
            from azure.identity.aio import DefaultAzureCredential
            credential = DefaultAzureCredential()
            client = ServiceBusClient(
                fully_qualified_namespace=settings.servicebus_namespace,
                credential=credential,
            )
        else:
            client = ServiceBusClient.from_connection_string(
                settings.servicebus_connection_string
            )

        async with client:
            sender = client.get_queue_sender(settings.servicebus_queue_name)
            async with sender:
                message = ServiceBusMessage(
                    body=json.dumps(message_body),
                    content_type="application/json",
                    message_id=f"order-{order_id}",  # idempotency key
                )
                await sender.send_messages(message)

        logger.info(
            "OrderCreated message published | order_id=%d | queue=%s",
            order_id,
            settings.servicebus_queue_name,
        )
        return True

    except Exception as exc:
        logger.error(
            "Failed to publish OrderCreated message | order_id=%d | error=%s",
            order_id,
            str(exc),
            exc_info=True,
        )
        return False
