# coding: utf-8

import click

from niamoto.exceptions import NoRecordFoundError, RecordAlreadyExistsError


@click.command("rasters")
def list_rasters_cli():
    """
    List registered rasters.
    """
    from niamoto.api import raster_api
    try:
        raster_df = raster_api.get_raster_list()
        if len(raster_df) == 0:
            click.echo("Niamoto raster database is empty.")
            return
        click.echo(raster_df.to_string(
            formatters={
                'date_create': format_datetime_to_date,
                'date_update': format_datetime_to_date,
            }
        ))
    except:
        click.echo("An error occurred, please ensure that Niamoto is "
                   "properly configured.")
        click.get_current_context().exit(code=1)


def format_datetime_to_date(obj):
    return obj.strftime("%Y/%m/%d")


@click.command('add_raster')
@click.option(
    '--srid',
    default=None,
    help='SRID of the raster. If not specified, it will be detected '
         'automatically.'
)
@click.argument('name')
@click.argument('tile_width')
@click.argument('tile_height')
@click.argument('raster_file_path')
def add_raster_cli(name, tile_width, tile_height, raster_file_path, srid=None):
    """
    Add a raster in Niamoto's raster database.
    """
    from niamoto.api import raster_api
    click.echo("Registering the raster in database...")
    try:
        raster_api.add_raster(
            raster_file_path,
            name,
            tile_width,
            tile_height,
            srid=srid,
        )
        click.echo("The raster had been successfully registered to the Niamoto"
                   " raster database!")
    except RecordAlreadyExistsError as e:
        click.secho(str(e), fg='red')
        click.get_current_context().exit(code=1)
    except:
        click.secho(
            "An error occurred while registering the raster.",
            fg='red'
        )
        click.get_current_context().exit(code=1)


@click.command('update_raster')
@click.option(
    '--srid',
    default=None,
    help='SRID of the raster. If not specified, it will be detected '
         'automatically.'
)
@click.argument('name')
@click.argument('tile_width')
@click.argument('tile_height')
@click.argument('raster_file_path')
def update_raster_cli(name, tile_width, tile_height, raster_file_path,
                      srid=None):
    """
    Update an existing raster in Niamoto's raster database.
    """
    from niamoto.api import raster_api
    click.echo("Updating {} raster...".format(name))
    try:
        raster_api.update_raster(
            raster_file_path,
            name,
            tile_width,
            tile_height,
            srid=srid,
        )
        click.echo("The raster had been successfully updated!")
    except NoRecordFoundError as e:
        click.secho(str(e), fg='red')
        click.get_current_context().exit(code=1)
    except:
        click.secho("An error occurred while updating the raster.", fg='red')
        click.get_current_context().exit(code=1)


@click.command('delete_raster')
@click.option('-y', default=False)
@click.argument('name')
def delete_raster_cli(name, y=False):
    """
    Delete an existing raster from Niamoto's raster database.
    """
    if not y:
        m = "If you continue, the raster will be deleted from the " \
            "database, are you sure you want to continue?"
        if not click.confirm(m, default=True):
            click.secho("Operation aborted.")
            return
    from niamoto.api import raster_api
    click.echo("Deleting {} raster...".format(name))
    try:
        raster_api.delete_raster(name)
        click.echo("The raster had been successfully deleted!")
    except NoRecordFoundError as e:
        click.secho(str(e), fg='red')
        click.get_current_context().exit(code=1)
    except:
        click.secho("An error occurred while deleting the raster.", fg='red')
        click.get_current_context().exit(code=1)
