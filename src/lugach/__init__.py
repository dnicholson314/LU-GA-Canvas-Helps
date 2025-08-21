import click

from lugach import interactive
from lugach.apps import app_names_and_descriptions, lint_app_name, run_app_from_app_name


@click.group()
def cli() -> None:
    """A CLI tool to make Liberty GAs lives easier."""


@cli.command()
@click.argument("app_name", required=False)
@click.option("--list", is_flag=True, help="List the currently available apps.")
@click.option("-i", is_flag=True, help="Run the interactive CLI.")
def app(app_name: str | None, i: bool | None, list: bool | None) -> None:
    """Run CLI applications to perform GSA tasks interactively.

    Use APP_NAME to specify the app to run. See --list for a list of apps.
    """

    if i:
        interactive.main()
        return

    if list:
        click.echo("The currently available apps: ")
        click.echo()

        for app_name, app_description in app_names_and_descriptions.items():
            click.echo(f"   {app_name:25} {app_description}")

        return

    if not app_name:
        click.echo("No APP_NAME supplied. Use --list for a list of apps.")
        return

    try:
        lint_app_name(app_name)
    except (TypeError, ValueError):
        click.echo("Invalid app name supplied. See --list for a list of apps.")
        return

    run_app_from_app_name(app_name)
