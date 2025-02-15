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

import os
import platform
from gen_vm_image.common.codes import SUCCESS
from gen_vm_image.cli.build_image import build_architecture
from libvirt_provider.utils.io import remove as fs_remove
from libvirt_provider.utils.user import (
    find_user_with_username,
    find_group_with_groupname,
)
from libvirt_provider.utils.io import join, exists, makedirs, load_json


CPU_ARCHITECTURE = platform.machine()
TEST_JINJA_TEMPLATE = "libvirt.j2"


class LibvirtTestContext:
    def __init__(self):
        self.init_done = False

    async def setUp(self):
        if self.init_done:
            return

        user_base = "qemu"
        self.user = find_user_with_username(user_base)
        assert self.user is not False
        self.group = find_group_with_groupname(user_base)
        assert self.group is not False

        self.architecture = CPU_ARCHITECTURE
        self.image_version = "12"
        self.name = f"libvirt-{self.architecture}"
        # Note, a properly SELinux labelled directory is required when SELinux is enabled
        self.images_dir = join("tests", "images", self.architecture)
        if not exists(self.images_dir):
            assert makedirs(self.images_dir)

        self.test_tmp_directory = os.path.realpath(join("tests", "tmp"))
        if not exists(self.test_tmp_directory):
            assert makedirs(self.test_tmp_directory)

        self.test_res_directory = os.path.realpath(join("tests", "res"))
        self.test_smoke_directory = os.path.realpath(join("tests", "smoke"))
        self.test_templates_directory = os.path.realpath(
            join(self.test_res_directory, "templates")
        )

        architecture_path = os.path.realpath(
            join(self.test_smoke_directory, "res", "gen-vm-image", "architecture.yml")
        )
        assert exists(architecture_path)
        self.image = join(self.images_dir, f"{self.name}-{self.image_version}.qcow2")
        return_code, msg = build_architecture(architecture_path, self.images_dir, False)
        assert return_code == SUCCESS
        assert exists(self.image)

        self.node_options_path = join(
            self.test_smoke_directory,
            "res",
            "node_options",
            f"{self.architecture}.json",
        )
        assert exists(self.node_options_path)
        self.common_node_options = load_json(self.node_options_path)
        assert isinstance(self.common_node_options, dict)

        self.init_done = True

    # Should be used by the non async function tearDownClass to ensure that
    # the following cleanup is done before the class is destroyed
    def tearDown(self):
        assert fs_remove(self.images_dir, recursive=True)
        assert fs_remove(self.test_tmp_directory, recursive=True)
