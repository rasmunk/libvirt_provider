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

import unittest
import pytest
import os
import random
from libvirt_provider.utils.io import copy, exists, join, load_json
from libvirt_provider.defaults import LIBVIRT
from libvirt_provider.client import new_client
from libvirt_provider.pool import Pool
from libvirt_provider.models import Node
from libvirt_provider.instance.create import create
from libvirt_provider.instance.remove import remove
from tests.context import LibvirtTestContext


@pytest.mark.smoke
class TestLibvirtPool(unittest.IsolatedAsyncioTestCase):
    context = LibvirtTestContext()

    async def asyncSetUp(self):
        await self.context.setUp()

        self.seed = str(random.random())[2:10]
        self.name = f"libvirt-pool-{self.context.architecture}-{self.seed}"

        self.test_image = os.path.realpath(f"{self.context.image}-{self.seed}")
        self.assertTrue(copy(self.context.image, self.test_image))
        self.assertTrue(exists(self.test_image))
        open_uri = "qemu:///session"
        self.client = new_client(LIBVIRT, open_uri=open_uri)

    async def asyncTearDown(self):
        # Ensure that any pool is destroyed
        pool = Pool(self.name)
        for node in await pool.items():
            removed, response = await remove(self.client, node.id)
            self.assertTrue(removed)

        self.assertTrue(await pool.flush())
        self.assertEqual(len(await pool.items()), 0)
        self.assertTrue(await pool.remove_persistence())
        self.client.close()

    @classmethod
    def tearDownClass(cls):
        cls.context.tearDown()

    async def test_libvirt_pool(self):
        # Load architecture node_options
        node_options_path = os.path.realpath(
            join(
                "tests",
                "smoke",
                "res",
                "node_options",
                f"{self.context.architecture}.json",
            )
        )
        self.assertTrue(exists(node_options_path))
        loaded_node_options = load_json(node_options_path)
        self.assertIsInstance(loaded_node_options, dict)

        pool = Pool(self.name)
        self.assertIsNotNone(pool)
        self.assertEqual(pool.name, self.name)
        self.assertEqual(len(await pool.items()), 0)

        node_name = f"libvirt-test-{self.seed}-node"
        node_options = {
            "name": node_name,
            "disk_image_path": self.test_image,
            "memory_size": "1024MiB",
            **loaded_node_options,
        }

        create_success, create_response = await create(self.client, **node_options)
        self.assertTrue(create_success)
        self.assertIn("instance", create_response)
        self.assertIsNotNone(create_response["instance"])
        node = create_response["instance"]

        self.assertIsInstance(node, Node)
        self.assertEqual(node.name, node_options["name"])
        self.assertTrue(await pool.add(node))
        self.assertEqual(len(await pool.items()), 1)

        pool_node = await pool.get(node.id)
        self.assertIsInstance(pool_node, Node)
        self.assertEqual(pool_node.name, node_options["name"])

        self.assertTrue(await pool.remove(node.id))
        self.assertFalse(await pool.get(node.id))
        self.assertEqual(len(await pool.items()), 0)

        removed, remove_response = await remove(self.client, node.id)
        self.assertTrue(removed)


if __name__ == "__main__":
    unittest.main()
