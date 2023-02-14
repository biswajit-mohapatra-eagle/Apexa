"""Entrypoint for cli commands."""

import logging

from apexa.cli.utils import click_group, click_option, click_pass_context
from apexa.common.util import get_logger

LOG = get_logger(__name__)


@click_group()
@click_option("--debug/--no--debug", help_message="Debug", default=False)
@click_pass_context()
def cli_command(ctx, debug: bool):
    """CLI entry point."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG if debug else logging.INFO)

    if ctx.obj is None:
        ctx.obj = {}

    ctx.obj["DEBUG"] = debug


def cli():
    """Start CLI interface."""
    try:
        cli_command()  # pylint: disable=E1120
    except KeyboardInterrupt as err:
        LOG.debug(f"{err}")
    except Exception as err:
        LOG.exception(f"{err}")
