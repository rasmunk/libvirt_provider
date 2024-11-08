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

PACKAGE_NAME = "libvirt_provider"

PROVIDER = "provider"
# Profile group defaults
PROFILE = "profile"
DRIVER = "driver"
PROFILE_DRIVER = "{}_{}".format(PROFILE, DRIVER)
LIBVIRT = "libvirt"
DUMMY = "dummy"
INSTANCE = "instance"
CONTAINER = "container"

INSTANCE_OPERATIONS = ["create", "ls", "remove", "show", "start", "stop", "purge"]
INSTANCE_CLI = {INSTANCE: INSTANCE_OPERATIONS}

CONTAINER_OPERATIONS = ["create", "ls", "remove", "show"]
CONTAINER_CLI = {CONTAINER: CONTAINER_OPERATIONS}

LIBVIRT_CLI_STRUCTURE = [INSTANCE_CLI, CONTAINER_CLI]

default_driver_config = {
    "uri": "test:///default",
    "key": None,
    "secret": None,
}

valid_driver_config = {"uri": str, "key": str, "secret": str}

default_config = {
    "name": "libvirt-provider",
    "type": "orchestration",
    "dependency_packages": [""],
    "driver": default_driver_config,
}

valid_default_config = {
    "name": str,
    "type": str,
    "dependency_packages": list,
    "driver": dict,
}

default_instance_config = {
    "name": "instance",
    "image": "",
    "size": "",
    "ssh_authorized_key": "",
}

valid_instance_config = {
    "name": str,
    "image": str,
    "size": str,
    "ssh_authorized_key": str,
}

# default_config = {
#     "instance": default_instance_config,
# }

# libvirt_default_config = {LIBVIRT: default_config}

# libvirt_valid_config = {
#     "profile": valid_profile_config,
#     "instance": valid_instance_config,
# }

# libvirt_config_groups = {
#     PROFILE: valid_profile_config,
#     PROFILE_DRIVER: valid_driver_config,
#     INSTANCE: valid_instance_config,
# }
