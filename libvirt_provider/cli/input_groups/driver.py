from libvirt_provider.defaults import INSTANCE, CONTAINER
from libvirt_provider.cli.parsers.driver import driver_group


def add_driver_group(parser, driver_type):
    if driver_type == INSTANCE:
        driver_group(parser, default_driver_uri="qemu:///system")
    if driver_type == CONTAINER:
        driver_group(parser, default_driver_uri="lxc:///")


def has_driver_group(libvirt_cli_type):
    if libvirt_cli_type == INSTANCE:
        return True
    if libvirt_cli_type == CONTAINER:
        return True
    return False
