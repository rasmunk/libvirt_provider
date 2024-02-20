from libvirt_provider.defaults import INSTANCE


def valid_create_group(parser):
    create_group(parser)


def create_group(parser):
    instance_group = parser.add_argument_group(title="Instance create arguments")
    instance_group.add_argument("name")
    instance_group.add_argument("disk_image_path")
    instance_group.add_argument(
        "-ms", "--memory-size", dest="{}_memory_size".format(INSTANCE)
    )


def remove_group(parser):
    instance_group = parser.add_argument_group(title="Instance remove arguments")
    instance_group.add_argument("name")
