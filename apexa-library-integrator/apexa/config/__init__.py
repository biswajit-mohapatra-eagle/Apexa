"""Integrator configuration management module."""

from typing import Optional, Union

from diskcache import Cache

from apexa.cli.utils import click_echo
from apexa.common.util import get_logger
from apexa.config.default import CACHE_DIR

LOG = get_logger(__name__)


class ConfigBaseException(Exception):
    """Base exception for config module."""

    def __init__(self, message="config file not found"):
        self.message = message
        super().__init__(self.message)


class Config:
    """Collector configuration management class."""

    def __init__(self):
        self.cache = Cache(CACHE_DIR)

    def get_cache(self, key: str) -> Union[dict, str]:
        """Returns the cache value for key.

        :param key: str cache key name
        :return: dict cache value
        """
        value = self.cache.get(key)
        if value:
            return value

        click_echo(
            "Rabbit Credentials are not set. "
            "Please set your credentials using `setup-rabbit` command.",
            color="yellow",
        )
        raise ConfigBaseException(f"Credential {key} is not set")

    def set_cache(
        self, key: str, value: Union[dict, str], expire: Optional[int] = None
    ) -> None:
        """sets the cache key with value.

        :param key: str cache key name
        :param value: dict cache value
        :param expire: int cache value expiration time
        :return: None
        :raises ConfigBaseException: if value is not a dict or str or bytes
         and value is not {} or "" or b""
        """
        if not (isinstance(value, (dict, str, bytes)) and value):
            # value is not a dict or str and value is not {} or ""
            raise ConfigBaseException(
                f"Setting {key} in cache as {value} is not supported"
            )
        return self.cache.set(key=key, value=value, expire=expire)

    def clear_cache(self) -> None:
        """Clear the cache."""
        return self.cache.clear()


config = Config()
