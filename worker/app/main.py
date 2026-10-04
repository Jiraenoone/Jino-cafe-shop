"""
worker/app/main.py — Jino Café Background Worker

Consumes 'OrderCreated' messages from Azure Service Bus queue.
Demonstrates decoupled asynchronous processing, retry handling, and observability.
"""
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load local environment variables if present
load_dotenv()

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | WORKER | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("jino-cafe-worker")

# Settings
SB_NAMESPACE = os.getenv("SERVICEBUS_NAMESPACE", "")
SB_QUEUE_NAME = os.getenv("SERVICEBUS_QUEUE_NAME", "order-created")
SB_CONN_STR = os.getenv("SERVICEBUS_CONNECTION_STRING", "")
APPINSIGHTS_CONN_STR = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")

# Telemetry
if APPINSIGHTS_CONN_STR:
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor(connection_string=APPINSIGHTS_CONN_STR)
        logger.info("Application Insights telemetry configured for worker")
    except Exception as e:
        logger.warning(f"Could not initialize App Insights: {e}")

# In-memory idempotency cache for deduplication
processed_message_ids = set()


async def process_order_message(data: dict, message_id: str) -> None:
    """
    Simulates sending an order confirmation email and background notification.
    """
    order_id = data.get("order_id")
    customer_email = data.get("customer_email")
    customer_name = data.get("customer_name")
    total_amount = data.get("total_amount")
    items_count = data.get("items_count")

    logger.info(
        f"Processing order #{order_id} for {customer_name} ({customer_email}) | Total: ฿{total_amount}"
    )

    # Simulate async work (e.g. SMTP transmission, PDF invoice generation)
    await asyncio.sleep(1.5)

    # Simulated Email Dispatch Output
    logger.info("=========================================================")
    logger.info(f"📧 [EMAIL DISPATCHED] To: {customer_email}")
    logger.info(f"Subject: Jino Café — Order Confirmation #{order_id}")
    logger.info("---------------------------------------------------------")
    logger.info(f"Dear {customer_name},")
    logger.info(f"Your handcrafted café order #{order_id} ({items_count} items) is being brewed.")
    logger.info(f"Total Amount: ฿{total_amount:.2f}")
    logger.info("Thank you for choosing Jino Café!")
    logger.info("=========================================================")


async def run_worker():
    logger.info("🚀 Jino Café Azure Service Bus Worker started")
    logger.info(f"Target Queue: {SB_QUEUE_NAME}")

    if not SB_CONN_STR and not SB_NAMESPACE:
        logger.warning(
            "⚠️ No Azure Service Bus credentials configured. "
            "Worker is idling in simulation standby mode. "
            "Set SERVICEBUS_CONNECTION_STRING or SERVICEBUS_NAMESPACE to connect to real Azure Service Bus."
        )
        while True:
            await asyncio.sleep(60)

    try:
        from azure.servicebus.aio import ServiceBusClient

        if SB_CONN_STR:
            client = ServiceBusClient.from_connection_string(SB_CONN_STR)
            logger.info("Connected to Service Bus via Connection String")
        else:
            from azure.identity.aio import DefaultAzureCredential
            credential = DefaultAzureCredential()
            client = ServiceBusClient(
                fully_qualified_namespace=SB_NAMESPACE,
                credential=credential
            )
            logger.info(f"Connected to Service Bus via Managed Identity ({SB_NAMESPACE})")

        async with client:
            receiver = client.get_queue_receiver(queue_name=SB_QUEUE_NAME)
            async with receiver:
                logger.info(f"Listening for messages on queue: '{SB_QUEUE_NAME}'...")

                while True:
                    messages = await receiver.receive_messages(max_message_count=10, max_wait_time=5)
                    for msg in messages:
                        msg_id = str(msg.message_id)

                        # Idempotency check
                        if msg_id in processed_message_ids:
                            logger.info(f"Duplicate message ignored: {msg_id}")
                            await receiver.complete_message(msg)
                            continue

                        try:
                            body_str = str(msg)
                            data = json.loads(body_str)
                            await process_order_message(data, msg_id)

                            processed_message_ids.add(msg_id)
                            # Settle message
                            await receiver.complete_message(msg)
                            logger.info(f"Message {msg_id} completed successfully")

                        except Exception as err:
                            logger.error(f"Error processing message {msg_id}: {err}", exc_info=True)
                            # Abandon message to allow redelivery according to queue retry policy
                            await receiver.abandon_message(msg)

    except Exception as err:
        logger.error(f"Fatal Service Bus worker exception: {err}", exc_info=True)
        await asyncio.sleep(10)


if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")
