from libvirt_provider.defaults import DRIVER, CONTAINER
from libvirt_provider.cli.parsers.container import (
    create_group,
    remove_group,
    list_group,
)


def create_groups(parser):
    create_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [CONTAINER]
    return provider_groups, argument_groups


def remove_groups(parser):
    remove_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [CONTAINER]
    return provider_groups, argument_groups


def list_groups(parser):
    list_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [CONTAINER]
    return provider_groups, argument_groups
