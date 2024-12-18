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


def valid_driver_group(parser):
    driver_group(parser)


def driver_group(
    parser,
    default_driver_name="libvirt",
    default_driver_uri="qemu:///session",
    default_driver_key=None,
    default_driver_secret=None,
):
    driver_group = parser.add_argument_group(title="Driver arguments")
    driver_group.add_argument("--driver-name", default=default_driver_name)
    driver_group.add_argument("--driver-uri", default=default_driver_uri)
    driver_group.add_argument("--driver-key", default=default_driver_key)
    driver_group.add_argument("--driver-secret", default=default_driver_secret)


def add_driver_group(
    parser,
    default_driver_name="libvirt",
    default_driver_uri="qemu:///session",
    default_driver_key=None,
    default_driver_secret=None,
):
    driver_group(
        parser,
        default_driver_name=default_driver_name,
        default_driver_uri=default_driver_uri,
        default_driver_key=default_driver_key,
        default_driver_secret=default_driver_secret,
    )
