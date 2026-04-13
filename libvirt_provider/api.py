import argparse

from libvirt_provider.cli.parsers.actions import PositionalArgumentsAction
from libvirt_provider.cli.parsers.instance import create_group


# TODO, expand to other functionality as well than creating an instance
def api():
    """Extract the default expected arguments and options from the argparser."""
    parser = argparse.ArgumentParser()
    create_group(parser)
    default_args = []
    default_options = {}

    for action in parser._actions:
        if isinstance(action, argparse._StoreAction):
            # Strip the leading double dash
            striped_key = action.option_strings[1].strip("--")
            key = striped_key.replace("-", "_")
            default_options[key] = action.default
        if isinstance(action, PositionalArgumentsAction):
            default_args.append(action.dest)
    return default_args, default_options
