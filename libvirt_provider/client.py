import libvirt
from libvirt_provider.defaults import LIBVIRT, DUMMY


def discover_provider_client(provider):
    if provider == LIBVIRT:
        return libvirt.open
    elif provider == DUMMY:
        pass
    else:
        raise RuntimeError("Unknown provider: {}".format(provider))


def load_client_options(*args, **kwargs):
    driver_args = []
    driver_kwargs = {}

    for arg in args:
        driver_args.append(arg)

    for key, value in kwargs.items():
        driver_kwargs[key] = value

    return driver_args, driver_kwargs


def new_client(provider, *args, **kwargs):
    # Discover driver
    driver = discover_provider_client(provider)
    driver_args, driver_kwargs = load_client_options(*args, **kwargs)
    return driver(*driver_args, **driver_kwargs)
