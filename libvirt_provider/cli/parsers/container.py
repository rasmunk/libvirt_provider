from libvirt_provider.defaults import CONTAINER
from libvirt_provider.cli.parsers.actions import PositionalArgumentsAction


def valid_create_group(parser):
    create_group(parser)


def valid_remove_group(parser):
    remove_group(parser)


def valid_list_group(parser):
    ls_group(parser)


def create_group(parser):
    container_group = parser.add_argument_group(title="Container create arguments")
    container_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the container"
    )
    container_group.add_argument(
        "-dt",
        "--domain-type",
        dest="{}_domain_type".format(CONTAINER),
        default="lxc",
        help="The domain type",
    )


def remove_group(parser):
    container_group = parser.add_argument_group(title="Container remove arguments")
    container_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the container"
    )


def show_group(parser):
    container_group = parser.add_argument_group(title="Container show arguments")
    container_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the container"
    )


def ls_group(parser):
    _ = parser.add_argument_group(title="Container list arguments")
