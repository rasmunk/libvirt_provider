def valid_instance_group(parser):
    instance_create_group(parser)


def instance_create_group(parser):
    instance_group = parser.add_argument_group(title="Instance arguments")
    instance_group.add_argument("name", default="")
    instance_group.add_argument("memory-size", default="")
    instance_group.add_argument("disk-image-path", default="")
