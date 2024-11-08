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

from libvirt_provider.defaults import CONTAINER
from libvirt_provider.cli.parsers.actions import PositionalArgumentsAction


def valid_create_group(parser):
    create_group(parser)


def valid_remove_group(parser):
    remove_group(parser)


def valid_list_group(parser):
    ls_group(parser)


def create_group(parser):
    container_group = parser.add_argument_group(title="Container create arguments")
    container_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the container"
    )
    container_group.add_argument(
        "-dt",
        "--domain-type",
        dest="{}_domain_type".format(CONTAINER),
        default="lxc",
        help="The domain type",
    )


def remove_group(parser):
    container_group = parser.add_argument_group(title="Container remove arguments")
    container_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the container"
    )


def show_group(parser):
    container_group = parser.add_argument_group(title="Container show arguments")
    container_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the container"
    )


def ls_group(parser):
    _ = parser.add_argument_group(title="Container list arguments")
