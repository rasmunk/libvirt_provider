from libvirt_provider.defaults import default_config


def load_driver_options(
    *args,
    **kwargs
):
    driver_args = []
    driver_kwargs = {}
    for arg in args:
        driver_args.append(arg)

    if "profile" in kwargs:
        if "driver" in kwargs["profile"]:
            provider_kwargs_driver = kwargs["profile"]["driver"]
            if "key" in provider_kwargs_driver and provider_kwargs_driver["key"]:
                driver_kwargs["key"] = provider_kwargs_driver["key"]

            if "secret" in provider_kwargs_driver and provider_kwargs_driver["secret"]:
                driver_kwargs["secret"] = provider_kwargs_driver["secret"]
    return driver_args, driver_kwargs


def generate_default_config():
    return default_config
