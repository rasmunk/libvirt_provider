from libvirt_provider.defaults import INSTANCE
from libvirt_provider.cli.parsers.actions import PositionalArgumentsAction


def valid_create_group(parser):
    create_group(parser)


def create_group(parser):
    instance_group = parser.add_argument_group(title="Instance create arguments")
    instance_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the instance"
    )
    instance_group.add_argument(
        "disk_image_path",
        action=PositionalArgumentsAction,
        help="The path to the disk image",
    )
    instance_group.add_argument(
        "-ms",
        "--memory-size",
        dest="{}_memory_size".format(INSTANCE),
        default="1024",
        help="The memory size of the instance",
    )


def remove_group(parser):
    instance_group = parser.add_argument_group(title="Instance remove arguments")
    instance_group.add_argument("id", help="The id of the instance to be removed")
