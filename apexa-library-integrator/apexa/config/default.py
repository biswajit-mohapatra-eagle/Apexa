"""Default configuration values."""

import os

SERVICE = "Scraper-Service"

PUBLISHER_MAX_RETRIES = 5
PUBLISHER_RETRY_INTERVAL = 5  # 5 seconds

SCRAPER_INTEGRATOR_DATA_EXCHANGE = "mdm_scraper_integrator_exchange_tp"
SCRAPER_INTEGRATOR_HARDWARE_ROUTING_KEY = "mdm.scraper.device.integrator"
SCRAPER_INTEGRATOR_SOFTWARE_ROUTING_KEY = "mdm.scraper.software.integrator"

DEFAULT_BASE_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".apexa")
BASE_CONFIG_DIR = os.environ.get("APEXADIR", DEFAULT_BASE_CONFIG_DIR)
CACHE_DIR = f"{BASE_CONFIG_DIR}/cache"
