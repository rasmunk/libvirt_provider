import asyncio
from libvirt_provider.client import new_client
from libvirt_provider.defaults import LIBVIRT


def get_argument_kwargs(arguments, groups=None):
    if not groups:
        groups = []

    argument_kwargs = {}
    for group in groups:
        if group in arguments:
            argument_kwargs[group] = getattr(arguments, group)
    return argument_kwargs


def get_argument_args(arguments, groups=None):
    if not groups:
        groups = []

    args = []
    for group in groups:
        if group in arguments:
            args.append(getattr(arguments, group))
    return args


def get_positional_args(arguments):
    args = []
    for arg in arguments:
        args.append(getattr(arguments, arg))
    return args


def import_from_module(module_path, module_name, func_name):
    module = __import__(module_path, fromlist=[module_name])
    return getattr(module, func_name)


def cli_exec(args):
    # action determines which function to execute
    module_path = args.module_path
    module_name = args.module_name
    func_name = args.func_name
    if hasattr(args, "provider_groups"):
        provider_groups = args.provider_groups
    else:
        provider_groups = []

    if hasattr(args, "argument_groups"):
        argument_groups = args.argument_groups
    else:
        argument_groups = []

    if hasattr(args, "skip_groups"):
        skip_groups = args.skip_groups
    else:
        skip_groups = []

    func = import_from_module(module_path, module_name, func_name)
    if not func:
        return False

    # Extract the arguments provided
    provider_args = get_argument_args(args, groups=provider_groups)
    provider_kwargs = get_argument_kwargs(args, groups=provider_groups)
    action_kwargs = get_argument_kwargs(args, groups=argument_groups)

    positional_args = get_positional_args(args)

    client = new_client(LIBVIRT, *provider_args, **provider_kwargs)
    return asyncio.run(func(client, action_kwargs))
