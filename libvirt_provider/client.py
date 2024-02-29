from libvirt_provider.defaults import LIBVIRT, CONTAINER, DUMMY
from libvirt_provider.models import DummyDriver, LibvirtDriver, LXCDriver


def discover_provider_client(provider):
    if provider == LIBVIRT:
        return LibvirtDriver
    if provider == CONTAINER:
        return LXCDriver
    elif provider == DUMMY:
        return DummyDriver
    else:
        raise RuntimeError("Unknown provider: {}".format(provider))


def new_client(provider, *args, **kwargs):
    # Discover driver
    driver = discover_provider_client(provider)
    return driver(*args, **kwargs)
