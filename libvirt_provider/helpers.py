from libcloud.compute.providers import get_driver
from libvirt_provider.config import load_driver_options


def discover_apache_driver(provider):
    return get_driver(provider)


def new_apache_client(provider, *args, **kwargs):
    # Discover driver
    driver = discover_apache_driver(provider)
    driver_args, driver_kwargs = load_driver_options(*args, **kwargs)
    return driver(*driver_args, **driver_kwargs)
