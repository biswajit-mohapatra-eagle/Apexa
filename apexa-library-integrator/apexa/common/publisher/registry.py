"""Registry to store retriable messages."""

from apexa.common.util import get_isoformated_date


class Registry:
    """Registry to store retriable messages."""

    def __init__(self):
        self.message_registry: dict = {}
        self.soft_delete_message_registry: list = []

    def add(
        self,
        request_id: str,
        msg: str,
        exchange: str,
        routing_key: str,
        service: str,
        retries: int = 0,
    ):
        """Add a message to registry.

        :param request_id: request id
        :param msg: message failed to send
        :param exchange: target exchange name
        :param routing_key: target queue routing key
        :service: current service name
        :retries: number of retries
        """
        self.message_registry[request_id] = {
            "msg": msg,
            "exchange": exchange,
            "routing_key": routing_key,
            "service": service,
            "retries": retries,
            "timestamp": get_isoformated_date(),
        }

    def increment_retries(self, request_id: str):
        """Increment retry count.

        :param request_id: request id
        """
        self.message_registry[request_id]["retries"] += 1

    def remove(self, request_id: str) -> dict:
        """Remove message from registry.

        :param request_id: request id
        """
        return self.message_registry.pop(request_id, None)

    def get_registry(self) -> dict:
        """Get complete registry.

        :returns complete registry
        """
        return self.message_registry

    def soft_delete_retry_message(self, request_id: str):
        """Soft delete successful retry message.

        :param request_id: request id
        """
        self.soft_delete_message_registry.append(request_id)

    def clear_soft_delete_retry_message(self):
        """Hard delete soft deleted retry message."""

        for message_id in self.soft_delete_message_registry:
            self.remove(message_id)
        self.soft_delete_message_registry = []


registry = Registry()
