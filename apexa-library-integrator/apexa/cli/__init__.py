"""Initalizes CLI interface."""

from apexa.cli import client  # pylint: disable=C0411
from apexa.cli.cli import cli, cli_command

__all__ = ["cli", "cli_command", "client"]
