from libvirt_provider.defaults import INSTANCE
from libvirt_provider.cli.parsers.actions import PositionalArgumentsAction


def valid_create_group(parser):
    create_group(parser)


def valid_list_group(parser):
    ls_group(parser)


def valid_remove_group(parser):
    remove_group(parser)


def valid_purge_group(parser):
    purge_group(parser)


def valid_show_group(parser):
    show_group(parser)


def valid_start_group(parser):
    start_group(parser)


def valid_stop_group(parser):
    stop_group(parser)


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
        "-ddn",
        "--disk-driver-name",
        dest="{}_disk_driver_name".format(INSTANCE),
        default="qemu",
        help="The disk driver name",
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
        default="vda",
        help="The disk target device",
    )
    instance_group.add_argument(
        "-dtb",
        "--disk-target-bus",
        dest="{}_disk_target_bus".format(INSTANCE),
        default="virtio",
        help="The disk target bus",
    )
    instance_group.add_argument(
        "-memory",
        "--memory-size",
        dest="{}_memory_size".format(INSTANCE),
        default="1024MiB",
        help="The memory size of the instance, interpreted as KiB. Default is 1024MiB.",
    )
    instance_group.add_argument(
        "-vcpus",
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
        "-cpu-mode",
        "--cpu-mode",
        dest="{}_cpu_mode".format(INSTANCE),
        default="host-model",
        help="The CPU mode to be used when running the instance",
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
        "-st",
        "--serial-type",
        dest="{}_serial_type".format(INSTANCE),
        default="pty",
        help="The serial type",
    )
    instance_group.add_argument(
        "-sttp",
        "--serial-type-target-port",
        dest="{}_serial_type_target_port".format(INSTANCE),
        default="0",
        help="The serial type target port",
    )
    instance_group.add_argument(
        "-tp",
        "--template-path",
        dest="{}_template_path".format(INSTANCE),
        help="The path to the XML template that should be used to create the instance.",
    )
    instance_group.add_argument(
        "-extra-tp-values",
        "--extra-template-path-values",
        metavar="KEY=VALUE",
        nargs="+",
        dest="{}_template_path_nargs".format(INSTANCE),
        default=[],
        help="""A set of key=value pair arguments that should be passed to the template.
        If a value contains spaces, you should define it with quotes.
        """,
    )


def remove_group(parser):
    instance_group = parser.add_argument_group(title="Instance remove arguments")
    instance_group.add_argument(
        "id",
        action=PositionalArgumentsAction,
        help="The id of the instance to be removed",
    )


def purge_group(parser):
    instance_group = parser.add_argument_group(
        title="Arguments for purging/removing multiple instances"
    )
    instance_group.add_argument(
        "-r",
        "--regex",
        dest="{}_regex".format(INSTANCE),
        default=None,
        help="Specify a regex that can be used to find the instances that should be removed",
    )
    instance_group.add_argument(
        "-f",
        "--force",
        dest="{}_force".format(INSTANCE),
        action="store_true",
        default=False,
        help="Whether instances that are running should also be stopped and removed",
    )


def show_group(parser):
    instance_group = parser.add_argument_group(title="Instance show arguments")
    instance_group.add_argument(
        "id",
        action=PositionalArgumentsAction,
        help="The id of the instance to be shown",
    )


def start_group(parser):
    instance_group = parser.add_argument_group(title="Instance start arguments")
    instance_group.add_argument(
        "id",
        action=PositionalArgumentsAction,
        help="The id of the instance to be started",
    )


def stop_group(parser):
    instance_group = parser.add_argument_group(title="Instance stop arguments")
    instance_group.add_argument(
        "id",
        action=PositionalArgumentsAction,
        help="The id of the instance to be stopped",
    )


def ls_group(parser):
    _ = parser.add_argument_group(title="Instance list arguments")
