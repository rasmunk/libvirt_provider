from libvirt_provider.defaults import DRIVER, CONTAINER
from libvirt_provider.cli.parsers.container import (
    create_group,
    remove_group,
    show_group,
    ls_group,
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


def show_groups(parser):
    show_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [CONTAINER]
    return provider_groups, argument_groups


def ls_groups(parser):
    ls_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [CONTAINER]
    return provider_groups, argument_groups
