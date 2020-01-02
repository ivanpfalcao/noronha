# -*- coding: utf-8 -*-

import click
import os

from noronha.api.note import NotebookAPI as API
from noronha.cli.handler import CMD
from noronha.common.constants import OnBoard, NoteConst
from noronha.common.utils import kv_list_to_dict


@click.command()
@click.option('--proj', help="Name of the project you'd like to work with")
@click.option(
    '--tag', '-t', default='latest',
    help="""The IDE runs on top of a Docker image that belongs to the project. """
    """You may specify the image's Docker tag or let it default to "latest\""""
)
@click.option(
    '--port', '-p', default=NoteConst.HOST_PORT,
    help="Host port that will be routed to the notebook's user interface (default: {})".format(NoteConst.HOST_PORT)
)
@click.option('--env-var', '-e', 'env_vars', multiple=True, help="Environment variable in the form KEY=VALUE")
@click.option(
    '--mount', '-m', 'mounts', multiple=True, help=
    """A host path or docker volume to mount on the IDE's container.\n"""
    """Syntax: <host_path_or_volume_name>:<container_path>:<rw/ro>\n"""
    """Example: /home/user/data:/data:rw"""
)
@click.option(
    '--edit', default=False, is_flag=True, help=
    """Flag: also mount current directory into the container's /app directory. This is useful if you want to """
    """edit code, test it and save it in the local machine (WARN: in Kubernetes mode this will only work if """
    """the current directory is part of your NFS server)"""
)
@click.option(
    '--dataset', '--ds', 'datasets',  multiple=True, help=
    """Reference to a dataset to be mounted on the IDE's container. """
    """Syntax: <model_name>:<dataset_name>. Example: iris-clf:iris-data-v0"""
)
@click.option(
    '--movers', '--mv', 'movers',  multiple=True, help=
    """Reference to a model version to be mounted on the IDE's container. """
    """Any flag in the third position means that this model is going to be used as a pre-trained asset. """
    """Syntax: <model_name>:<version_name>:<is_pretrained>. Example: word2vec:en-us-v1:true"""
)
@click.option(
    '--resource-profile', '--rp', 'resource_profile', help=
    """Name of a resource profile to be applied for each container. """
    """This profile should be configured in your nha.yaml file"""
)
def note(env_vars: list, mounts: list, port: int, edit: bool = False, **kwargs):
    
    """Access to the Jupyter Notebook (IDE)"""
    
    edit_mount = ['{}:{}:rw'.format(os.getcwd(), OnBoard.APP_HOME)] if edit else []
    
    CMD.run(
        API, '__call__', **kwargs,
        env_vars=kv_list_to_dict(env_vars),
        mounts=list(mounts) + edit_mount,
        port=int(port)
    )
