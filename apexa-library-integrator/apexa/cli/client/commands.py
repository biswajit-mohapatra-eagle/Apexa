"""Apexa CLI commands."""

from apexa.cli.cli import cli_command
from apexa.cli.utils import (
    CustomCommand,
    click_echo,
    click_option,
    click_option_choice,
    click_promt,
)
from apexa.common.controller import scraper_controller
from apexa.common.util import metadata_entry_points
from apexa.config import config

SCRAPPER_ENTRY_POINT_GROUP = "apexa-library-integrator.source"
SCRAPPER_SOURCES = {
    e.name: e for e in metadata_entry_points().select(group=SCRAPPER_ENTRY_POINT_GROUP)
}
RABBIT_CREDS = ["RABBIT_HOST", "RABBIT_PORT", "RABBIT_USER", "RABBIT_PASSWORD"]


@cli_command.command(cls=CustomCommand)
@click_option(
    "--scrappers",
    help_message="Scraper names to be run",
    show_default=True,
    type=click_option_choice(SCRAPPER_SOURCES.keys(), case_sensitive=False),
)
@click_option(
    "--test",
    is_flag=True,
    default=False,
    help_message="Run a single scrapper test",
    show_default=True,
)
@click_option(
    "--output-type",
    default="csv",
    help_message="Output file type",
    show_default=True,
    type=click_option_choice(["JSON", "CSV"], case_sensitive=False),
)
def scrape(scrappers: str, test: bool, output_type: str):
    """Run scrappers."""
    click_echo("Running scrappers", color="green")
    scrappers = scrappers.split(",") if scrappers else []
    scraper_controller.run_scrappers(scrappers, test, output_type)
    click_echo("Done!", color="green")


@cli_command.command(cls=CustomCommand)
@click_option(
    "--property",
    help_message="Set individual rabbit credentials",
    type=click_option_choice(RABBIT_CREDS, case_sensitive=True),
)
def setup_rabbit(property):
    """Set up credentials for rabbitmq."""
    if property:
        input_value = click_promt(f"Enter {property}")
        config.set_cache(property, input_value)
    else:
        for cred in RABBIT_CREDS:
            input_value = click_promt(f"Enter {cred}")
            config.set_cache(cred, input_value)
