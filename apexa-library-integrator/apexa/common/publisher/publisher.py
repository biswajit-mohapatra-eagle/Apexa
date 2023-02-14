"""Publisher utility with retry logic."""

# Imports
from typing import Union

from pika import ConnectionParameters, PlainCredentials, SelectConnection, spec

from apexa.common.publisher.registry import registry
from apexa.common.util import get_logger, sleep_seconds
from apexa.config import config
from apexa.config.default import (
    PUBLISHER_MAX_RETRIES,
    PUBLISHER_RETRY_INTERVAL,
    SERVICE,
)

logger = get_logger(__name__)


def init_pika_connection(host, port, user, password, on_open_callback):
    """Init Pika connection.

    :param host: Rabbit host name
    :param port: Rabbit port number
    :param user: Rabbit user name
    :param password: Rabbit password
    :param on_open_callback: Callback function when connection is opened

    :returns pika rabbitMQ connection object
    """
    credentials = PlainCredentials(user, password)
    parameters = ConnectionParameters(host, port, "/", credentials, heartbeat=60)
    connection = SelectConnection(
        parameters=parameters, on_open_callback=on_open_callback
    )
    return connection


# Publish a message
def publish(
    exchange: str, routing_key: str, msg: str, request_id: str, is_retry: bool = False
):
    """Publish message and keep track of ACK|NACK for the event.

    :param exchange : Exchange name to be published on
    :param routing_key : Routing Key for exchange
    :param msg : Message payload to be published
    :param request_id: ID of the request message
    :param is_retry : Publish retry attemp?. Defaults to False.
    """
    # Rabbit configuration
    rabbit_user = config.get_cache("RABBIT_USER")
    rabbit_password = config.get_cache("RABBIT_PASSWORD")
    rabbit_host = config.get_cache("RABBIT_HOST")
    rabbit_port = config.get_cache("RABBIT_PORT")

    def on_open(conn):
        """After Connection is opened, create a channel."""
        conn.channel(on_open_callback=on_channel_open)

    def on_channel_open(channel):
        """After channel is open, publish message."""
        channel.confirm_delivery(ack_nack_callback=on_delivery_confirmation)

        try:
            channel.basic_publish(exchange, routing_key, body=msg)
        except Exception as err:
            # Error while publishing (other than NACK)
            logger.error(
                f"[{request_id}] Error While Publishing to: "
                f"'{exchange}' with '{routing_key}' | ERROR: {err}"
            )
            raise

    def on_delivery_confirmation(frame):
        """Delivery Confermation after publishing message."""
        # Got ACK
        if isinstance(frame.method, spec.Basic.Ack):
            # Remove message from map if got ACK for retried message
            if is_retry:
                registry.soft_delete_retry_message(request_id)

        # Got NACK
        else:
            registry.add(
                request_id, msg, exchange, routing_key, SERVICE
            )  # Add message to map
            logger.error(
                f"[{request_id}] Failed to publish to: "
                f"'{exchange}' with '{routing_key}'"
            )

        # Close Connection
        connection.close()
        connection.ioloop.stop()

    # Intialized Connection
    connection = init_pika_connection(
        rabbit_host, rabbit_port, rabbit_user, rabbit_password, on_open
    )

    # Cannot connect to RabbitMQ
    if not connection:
        logger.error(
            f"[{request_id}] Unable to Publish. "
            "Broken or Uninitialized RabbitMQ Connection"
        )
    else:
        connection.ioloop.start()


# Retry after "5" sec interval
def retry():
    """Retry Failed Publish Message."""

    underliverables = []
    retriable_messages = registry.get_registry()

    for request_id, msg in retriable_messages.items():
        if msg["retries"] < PUBLISHER_MAX_RETRIES:
            registry.increment_retries(request_id)
            exchange, routing_key = msg["exchange"], msg["routing_key"]

            logger.info(
                f"Retrying failed messages to: '{exchange}' with '{routing_key}'"
            )
            publish(
                exchange,
                routing_key,
                msg=msg["msg"],
                is_retry=True,
                request_id=request_id,
            )
        else:
            # Move to notification queue
            underliverables.append(request_id)
            logger.warning(
                "Retrying Failed for Below Message! "
                f"Publishing to Notification Service. {underliverables}"
            )
    registry.clear_soft_delete_retry_message()
    if underliverables:
        underliverables = [
            registry.remove(request_id) for request_id in underliverables
        ]


def publish_messages(
    exchange: str, routing_key: str, msg: Union[str, bytes], request_id: str
) -> str:
    """Publish function that intiates publishing and handles retrying.

    :param exchange: Exchange to be published on
    :param routing_key: Routing key for exchange
    :param msg: Message to be published
    :param request_id: ID of the request message
    :returns "Done" response message
    """

    if isinstance(msg, (str, bytes)):
        msgs = [msg]
    else:
        msgs = msg

    for message in msgs:
        publish(exchange, routing_key, msg=message, request_id=request_id)  # Publish

    # Check for retries
    while len(registry.get_registry()):
        sleep_seconds(PUBLISHER_RETRY_INTERVAL)
        retry()  # Retry

    return "Done"
