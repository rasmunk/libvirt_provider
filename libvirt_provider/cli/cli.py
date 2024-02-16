import argparse
import datetime
import json
from libvirt_provider.utils.format import eprint
from libvirt_provider.defaults import PACKAGE_NAME, DRIVER
from libvirt_provider.cli.helpers import cli_exec, import_from_module
from libvirt_provider.cli.parsers.driver import driver_group


def to_str(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def driver_cli(parser):
    driver_group(parser)


def functions_cli(
    parser,
    module_cli_prefix="{}.cli.parsers".format(PACKAGE_NAME),
):
    actions = ["create", "remove", "start", "stop", "state", "get"]
    for action in actions:
        sub_parser = parser.add_parser(
            action, help="{} a VM".format(action.capitalize())
        )

        operation_input_groups_func = import_from_module(
            module_cli_prefix, "instance", operation
        )

        argument_groups = []
        skip_groups = []
        input_groups = operation_input_groups_func(operation_parser)
        if not input_groups:
            raise RuntimeError(
                "No input groups were returned by the input group function: {}".format(
                    operation_input_groups_func.func_name
                )
            )

        if len(input_groups) == 2:
            argument_groups = input_groups[1]
            skip_groups = input_groups[2]
        else:
            # Only a single datatype was returned
            # and therefore should no longer be a tuple
            argument_groups = input_groups

        sub_parser.set_defaults(
            func=cli_exec,
            module_path="libvirt_provider.instance",
            module_name="instance",
            func_name=action,
            provider_groups=[DRIVER],
            argument_groups=argument_groups,
            skip_groups=skip_groups,
        )


def run():
    parser = argparse.ArgumentParser(prog=PACKAGE_NAME)
    driver_cli(parser)
    commands = parser.add_subparsers(title="COMMAND")
    # Add corc functions to the CLI
    functions_cli(commands)
    args = parser.parse_args()

    # Execute default function
    if hasattr(args, "func"):
        success, response = args.func(args)
        output = ""
        if success:
            response["status"] = "success"
        else:
            response["status"] = "failed"

        try:
            output = json.dumps(response, indent=4, sort_keys=True, default=to_str)
        except Exception as err:
            eprint("Failed to format: {}, err: {}".format(output, err))
        if success:
            print(output)
        else:
            eprint(output)
    return None


if __name__ == "__main__":
    arguments = run()
