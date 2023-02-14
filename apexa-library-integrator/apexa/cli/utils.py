"""CLI Utilities."""

from typing import Iterable, Union

import click
from click import Context, HelpFormatter

from apexa.common.util import APP_NAME, CONFIG_CONTEXT, json_dumps

CLI_FILE_NAME = "run.py"


def click_group():
    """Initialize click group."""
    return click.group(
        cls=CustomGroup,
        context_settings=CONFIG_CONTEXT["context_settings"],
    )


def click_option(name: str, help_message: str, **kwargs):
    """Set click command options.

    :param name: Command Options name
    :param help_message: Command Options help
    :param kwargs: Command Options kwargs
    """
    return click.option(name, help=help_message, **kwargs)


def click_pass_context() -> Context:
    """Return a click context."""
    return click.pass_context


def click_option_choice(choices: Iterable, case_sensitive: bool):
    """Return click command option choices parser.

    :param choices: Command Options choices
    :param case_sensitive: Case sensitivity while reading options
    """
    return click.Choice(choices, case_sensitive)


def click_echo(text: str, color: str):
    """Print text on console.

    :param text: Text to print
    :param color: Text color
    """
    click.secho(text, fg=color)


# click related functions
def click_echo_json(obj: Union[dict, list]) -> None:
    """Echo json to click output.

    :param obj: dict
    """
    click.echo(json_dumps(obj, indent=2))


def click_promt(text: str):
    """Click prompt on console and return input.

    :param text: Input text instruction
    :returns Input text
    """
    return click.prompt(text)


def intialize_context(**kwargs):
    """Intialize context.

    :param kwargs: Keyword arguments
    """
    if "context_settings" not in kwargs:
        kwargs["context_settings"] = CONFIG_CONTEXT["context_settings"]


def _format_usage(ctx: Context, formatter: HelpFormatter, pieces: list[str]):
    """Format usage helper function.

    :param ctx: Click Context
    :param formatter: Help text message formatter
    :param pieces: Pieces that go into the usage line
    """
    custom_name = ctx.command_path.replace(CLI_FILE_NAME, APP_NAME)
    formatter.write_usage(
        prog=custom_name,
        args=" ".join(pieces),
    )


class CustomGroup(click.Group):
    """Custom Group to provide a custom help message."""

    def __init__(self, *args, **kwargs):
        """Initialize the Group.

        :param args: args
        :param kwargs: kwargs
        """
        intialize_context(**kwargs)
        super().__init__(*args, **kwargs)

    def format_usage(self, ctx: Context, formatter: HelpFormatter) -> None:
        """Writes the usage line into the formatter.

        This is a low-level method called by :meth:`get_usage`.
        """
        pieces = self.collect_usage_pieces(ctx)
        _format_usage(ctx, formatter, pieces)


class CustomCommand(click.Command):
    """Custom Command to provide a custom help message."""

    def __init__(self, *args, **kwargs):
        """Initialize the Command.

        :param args: args
        :param kwargs: kwargs
        """
        intialize_context(**kwargs)
        super().__init__(*args, **kwargs)

    def format_usage(self, ctx: Context, formatter: HelpFormatter) -> None:
        """Writes the usage line into the formatter.

        This is a low-level method called by :meth:`get_usage`.
        """
        pieces = self.collect_usage_pieces(ctx)
        _format_usage(ctx, formatter, pieces)
