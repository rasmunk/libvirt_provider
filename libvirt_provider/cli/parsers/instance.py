def valid_create_group(parser):
    create_group(parser)


def create_group(parser):
    instance_group = parser.add_argument_group(title="Instance create arguments")
    instance_group.add_argument("name")
    instance_group.add_argument("disk-image-path")
    instance_group.add_argument("-ms", "--memory-size")


def remove_group(parser):
    instance_group = parser.add_argument_group(title="Instance remove arguments")
    instance_group.add_argument("name", default="")
