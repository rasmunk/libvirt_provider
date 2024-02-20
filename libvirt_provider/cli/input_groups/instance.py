from libvirt_provider.defaults import DRIVER, INSTANCE
from libvirt_provider.cli.parsers.instance import create_group, remove_group


def create_groups(parser):
    create_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [INSTANCE]
    return provider_groups, argument_groups


def remove_groups(parser):
    remove_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [INSTANCE]
    return provider_groups, argument_groups
