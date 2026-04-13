# Copyright (C) 2024  rasmunk
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

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
