import click
import logging
from os.path import join
from os import getcwd, environ

# modify the local path so we can import our env.py
WORKING_DIR = getcwd()



@click.group()
@click.option('--log', default='INFO', help='Set the log level. DEBUG, INFO, WARNING, ERROR.')
def cli(log):
    level = getattr(logging, log.upper())
    logging.basicConfig(level=level)


@cli.command()
@click.option('--server', default=None, help='Path to server connection file')
@click.option('--compare', default=None, help='Branch to compare to publishing status')
@click.option('--empty', default='empty.aprx', help='Empty pro project to use for importing map files')
@click.option('--temp', default='temp.aprx', help='Temp pro project to save as for importing map files')
def publish(server=None, compare=None, empty='empty.aprx', temp='temp.aprx'):
    """
    Publish all updated maps in the local ./maps/ directory. 
    Map files will be compared to <branch> name. 
    Local branch will be updated after publishing. 
    """
    logging.info('Importing arcpy...please wait...')
    from git import Repo
    from .publish import publish
    import arcpy

    # create a temporary working project
    logging.info('Opening pro project {}'.format(empty))
    project = arcpy.mp.ArcGISProject(empty)
    logging.info('Creating temporary pro project {}'.format(temp))
    project.saveACopy(temp)
    project = arcpy.mp.ArcGISProject(temp)

    # get a repo instance and get the files changed list
    repo = Repo(WORKING_DIR)
    all_items = [item.a_path for item in repo.index.diff(compare)] + repo.untracked_files
    updated_map_paths = [item for item in all_items if '.mapx' in item]
    map_items = []

    # update a new temp project with the map files that changed
    for item in updated_map_paths:
        parts = item.split('/')
        logging.info('Importing map file {}'.format(item))
        project.importDocument(item)
        map_items.append({
            'name': parts[-1].replace('.mapx', ''),
            'folder': parts[1] if len(parts) == 3 else None,
        })

    logging.info('Saving updated temp project')
    project.save()

    logging.info("""
        Starting publishing process. 
        Services will be published to {}
    """.format(server))
    for item in map_items:
        name = item['name']
        folder = item['folder']
        logging.info('Publishing map service: {}/{}'.format(folder, name))
        publish(
            map_name=name,
            server=server,
            service_name=name,
            folder=folder,
            overwrite=True,
            feature_access=True,
            instance_count=0,
            project=project,
        )
        logging.info('Service published successfully')

if __name__ == '__main__':
    logging.info('Current working directory is {}'.format(WORKING_DIR))
    init_migrations(WORKING_DIR)

    # create cli with context
    cli()
