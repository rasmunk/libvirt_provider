from libvirt_provider.defaults import DRIVER
from libvirt_provider.cli.parsers.instance import instance_create_group

def add_instance_group(parser):
    instance_create_group(parser)

    provider_groups = [DRIVER]
    argument_groups = []
    skip_groups = []
    return provider_groups, argument_groups, skip_groups
