"""Publisher Dependancy for service which handles all publish operations."""

from apexa.common.publisher import publisher
from apexa.common.util import (
    generate_uuid,
    get_isoformated_date,
    get_logger,
    json_dumps,
    logging,
)
from apexa.config.default import (
    SCRAPER_INTEGRATOR_DATA_EXCHANGE,
    SCRAPER_INTEGRATOR_HARDWARE_ROUTING_KEY,
    SCRAPER_INTEGRATOR_SOFTWARE_ROUTING_KEY,
)

logger = get_logger(__name__)
get_logger("pika").setLevel(logging.WARNING)


class Publisher:
    """Publlisher Functions."""

    def __init__(self):
        pass

    def publish_scraper_data(self, data: dict, routing_key: str):
        """Publish scraped hardware data.

        :param data: Scraped data
        :param routing_key: Routing key, software/hardware
        """
        request_id = generate_uuid()

        # Generate Payload
        payload = {
            "requestId": request_id,
            "eol_data": data,
            "timestamp": get_isoformated_date(),
        }

        payload = json_dumps(payload)

        # Publish!
        logger.info(
            f"[{request_id}] Publishing Scraped data to: "
            f"'{SCRAPER_INTEGRATOR_DATA_EXCHANGE}' with "
            f"'{routing_key}'"
        )

        publisher.publish_messages(
            exchange=SCRAPER_INTEGRATOR_DATA_EXCHANGE,
            routing_key=routing_key,
            msg=payload,
            request_id=request_id,
        )

        logger.info(
            f"[{request_id}] Published Scraped data to: "
            f"'{SCRAPER_INTEGRATOR_DATA_EXCHANGE}' with "
            f"'{routing_key}'"
        )

    def publish_software_scraper_data(self, data: dict):
        """Publish scraped software data.

        :param data: Scraped software data
        """
        self.publish_scraper_data(data, SCRAPER_INTEGRATOR_SOFTWARE_ROUTING_KEY)

    def publish_hardware_scraper_data(self, data):
        """Publish scraped Hardware data.

        :param data: Scraped Hardware data
        """
        self.publish_scraper_data(data, SCRAPER_INTEGRATOR_HARDWARE_ROUTING_KEY)
