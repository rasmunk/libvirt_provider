from libvirt_provider.defaults import LIBVIRT, DUMMY
from libvirt_provider.models import DummyDriver, LibvirtDriver


def discover_provider_client(provider):
    if provider == LIBVIRT:
        return LibvirtDriver
    elif provider == DUMMY:
        return DummyDriver
    else:
        raise RuntimeError("Unknown provider: {}".format(provider))


def new_client(provider, *args, **kwargs):
    # Discover driver
    driver = discover_provider_client(provider)
    return driver(*args, **kwargs)
