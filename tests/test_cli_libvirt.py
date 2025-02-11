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
import unittest
import random
from libvirt_provider.defaults import INSTANCE
from libvirt_provider.codes import SUCCESS
from libvirt_provider.cli.cli import main
from libvirt_provider.utils.io import copy, exists
from tests.context import LibvirtTestContext


class TestCLILibvirt(unittest.IsolatedAsyncioTestCase):
    context = LibvirtTestContext()

    async def asyncSetUp(self):
        await self.context.setUp()

        self.seed = str(random.random())[2:10]
        self.name = f"libvirt-cli-libvirt-{self.context.architecture}-{self.seed}"

        self.test_image = os.path.realpath(f"{self.context.image}-{self.seed}")
        self.assertTrue(copy(self.context.image, self.test_image))
        self.assertTrue(exists(self.test_image))

        self.common_instance_args = [
            "--{} {}".format(option, value)
            for option, value in self.context.common_node_options.items()
        ]

    @classmethod
    def tearDownClass(cls):
        cls.context.tearDown()

    def test_cli_create_instance(self):
        return_code = None
        try:
            name = "test-cli-create-instance-{}".format(self.seed)
            return_code = main(
                [INSTANCE, "create", name, self.test_image].extend(
                    self.common_instance_args
                )
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)
