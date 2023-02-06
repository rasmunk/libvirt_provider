default_driver_config = {
    "uri": "test:///default",
    "key": None,
    "secret": None,
}

valid_driver_config = {"uri": str, "key": str, "secret": str}

default_config = {
    "name": "libvirt-provider",
    "type": "orchestration",
    "dependency_packages": ["libcloud"],
    "driver": default_driver_config,
}

valid_default_config = {
    "name": str,
    "type": str,
    "dependency_packages": list,
    "driver": dict,
}
