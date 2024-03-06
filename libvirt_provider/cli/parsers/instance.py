from libvirt_provider.defaults import INSTANCE
from libvirt_provider.cli.parsers.actions import PositionalArgumentsAction


def valid_create_group(parser):
    create_group(parser)


def valid_remove_group(parser):
    remove_group(parser)


def valid_list_group(parser):
    ls_group(parser)


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
        "-dt",
        "--domain-type",
        dest="{}_domain_type".format(INSTANCE),
        default="kvm",
        help="The domain type",
    )
    instance_group.add_argument(
        "-ddtype",
        "--disk-device-type",
        dest="{}_disk_device_type".format(INSTANCE),
        default="file",
        help="The disk type",
    )
    instance_group.add_argument(
        "-ddt",
        "--disk-driver-type",
        dest="{}_disk_driver_type".format(INSTANCE),
        default="qcow2",
        help="The disk driver type",
    )
    instance_group.add_argument(
        "-dtd",
        "--disk-target-dev",
        dest="{}_disk_target_dev".format(INSTANCE),
        default="hda",
        help="The disk target device",
    )
    instance_group.add_argument(
        "-dtb",
        "--disk-target-bus",
        dest="{}_disk_target_bus".format(INSTANCE),
        default="ide",
        help="The disk target bus",
    )
    instance_group.add_argument(
        "-ms",
        "--memory-size",
        dest="{}_memory_size".format(INSTANCE),
        default="1024MiB",
        help="The memory size of the instance, interpreted as KiB. Default is 1024MiB.",
    )
    instance_group.add_argument(
        "-vs",
        "--num-vcpus",
        dest="{}_num_vcpus".format(INSTANCE),
        default="1",
        help="The number of virtual CPUs",
    )
    instance_group.add_argument(
        "-cpu-arch",
        "--cpu-architecture",
        dest="{}_cpu_architecture".format(INSTANCE),
        default="x86_64",
        help="The CPU architecture",
    )
    instance_group.add_argument(
        "-mach",
        "--machine",
        dest="{}_machine".format(INSTANCE),
        default="pc",
        help="The machine type",
    )
    instance_group.add_argument(
        "-ct",
        "--console-type",
        dest="{}_console_type".format(INSTANCE),
        default="pty",
        help="The console type",
    )
    instance_group.add_argument(
        "-tp",
        "--template-path",
        dest="{}_template_path".format(INSTANCE),
        help="The path to the XML template that should be used to create the instance.",
    )


def remove_group(parser):
    instance_group = parser.add_argument_group(title="Instance remove arguments")
    instance_group.add_argument(
        "id",
        action=PositionalArgumentsAction,
        help="The id of the instance to be removed",
    )


def show_group(parser):
    instance_group = parser.add_argument_group(title="Instance show arguments")
    instance_group.add_argument(
        "id",
        action=PositionalArgumentsAction,
        help="The id of the instance to be shown",
    )


def ls_group(parser):
    _ = parser.add_argument_group(title="Instance list arguments")
