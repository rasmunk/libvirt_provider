from libvirt_provider.defaults import DRIVER, INSTANCE
from libvirt_provider.cli.parsers.instance import (
    create_group,
    ls_group,
    remove_group,
    purge_group,
    show_group,
    start_group,
    stop_group,
)


def create_groups(parser):
    create_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [INSTANCE]
    return provider_groups, argument_groups


def ls_groups(parser):
    ls_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [INSTANCE]
    return provider_groups, argument_groups


def purge_groups(parser):
    purge_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [INSTANCE]
    return provider_groups, argument_groups


def remove_groups(parser):
    remove_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [INSTANCE]
    return provider_groups, argument_groups


def show_groups(parser):
    show_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [INSTANCE]
    return provider_groups, argument_groups


def start_groups(parser):
    start_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [INSTANCE]
    return provider_groups, argument_groups


def stop_groups(parser):
    stop_group(parser)

    provider_groups = [DRIVER]
    argument_groups = [INSTANCE]
    return provider_groups, argument_groups
