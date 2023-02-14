"""Initialize CLI commands."""

from apexa.cli.cli import cli_command
from apexa.cli.client.commands import scrape

cli_command.add_command(scrape)
