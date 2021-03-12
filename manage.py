"""Database management utilities"""

import asyncio
import os
import traceback

import click
from tornado.options import options

import server.app
import server.databases


APP_ROOT = os.path.dirname(server.__file__)


@click.group()
def cli():
    pass


@cli.group()
def db():
    pass


# @db.command()
# def init():
#     options.parse_config_file(os.path.join(APP_ROOT, "config/app.conf"))

#     run = asyncio.get_event_loop().run_until_complete

#     try:
#         Database = server.databases.database_types[options.db_type]
#     except KeyError:
#         click.echo("Invalid db_type provided.", err=True)
#         return

#     db = Database()

#     try:
#         run(db.prepare())
#     except Exception:
#         click.echo(
#             f"Could not connect to database.\n{traceback.format_exc()}",
#             err=True,
#         )
#         return

#     if run(db.is_initialized()):
#         click.echo("Database is already initialized. Run 'db delete' to delete the database.")
#         return

#     try:
#         # TODO: generate roles n stuff
#         run(db.initialize())
#     except Exception:
#         click.echo(
#             f"Could initialize the database.\n{traceback.format_exc()}",
#             err=True,
#         )
#         return

@db.command()
def delete():
    options.parse_config_file(os.path.join(APP_ROOT, "config/app.conf"))

    run = asyncio.get_event_loop().run_until_complete

    try:
        Database = server.databases.database_types[options.db_type]
    except KeyError:
        click.echo("Invalid db_type provided.", err=True)
        return

    db = Database()

    try:
        run(db.prepare())
    except Exception:
        click.echo(
            f"Could not connect to the database.\n{traceback.format_exc()}",
            err=True,
        )
        return

    if not run(db.is_initialized()):
        click.confirm("Database is not initialized. Continue with deletion?", abort=True)

    click.confirm("Are you sure you want to delete the database? This is not reversible.", abort=True)

    try:
        run(db.delete())
    except Exception:
        click.echo(
            f"Could not delete the database.\n{traceback.format_exc()}",
            err=True,
        )
        return

    click.echo("Deleted the database.")


if __name__ == "__main__":
    cli()
