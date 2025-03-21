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
from libvirt_provider.defaults import DUMMY
from libvirt_provider.client import new_client
from libvirt_provider.pool import Pool
from libvirt_provider.models import Node
from libvirt_provider.instance.create import create
from libvirt_provider.instance.remove import remove


class TestDummyPool(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.name = "dummy-pool"
        self.client = new_client(DUMMY)

    async def asyncTearDown(self):
        # Ensure that any pool is destroyed
        pool = Pool(self.name)
        for node in await pool.items():
            removed, response = await remove(self.client, node.id)
            self.assertTrue(removed)
        self.assertTrue(await pool.flush())
        self.assertEqual(len(await pool.items()), 0)
        self.assertTrue(await pool.remove_persistence())

    async def test_dummy_pool(self):
        pool = Pool(self.name)
        self.assertIsNotNone(pool)
        self.assertEqual(pool.name, self.name)

        node_options_1 = {
            "name": "dummy-test-1",
            "image": "Test Image",
            "size": "Small",
        }
        node_options_2 = {
            "name": "dummy-test-2",
            "image": "Test Image",
            "size": "Medium",
        }
        node_options_3 = {
            "name": "dummy-test-3",
            "image": "Test Image",
            "size": "Large",
        }

        created1, response1 = await create(self.client, **node_options_1)
        self.assertTrue(created1)
        self.assertTrue(await pool.add(response1["instance"]))

        created2, response2 = await create(self.client, **node_options_2)
        self.assertTrue(created2)
        self.assertTrue(await pool.add(response2["instance"]))

        created3, response3 = await create(self.client, **node_options_3)
        self.assertTrue(created3)
        self.assertTrue(await pool.add(response3["instance"]))

        nodes = sorted(await pool.items(), key=lambda node: node.name)
        self.assertEqual(len(nodes), 3)

        for node in nodes:
            self.assertIsInstance(node, Node)

        self.assertEqual(nodes[0].name, node_options_1["name"])
        self.assertEqual(nodes[0].config["image"], node_options_1["image"])
        self.assertEqual(nodes[0].config["size"], node_options_1["size"])

        self.assertEqual(nodes[1].name, node_options_2["name"])
        self.assertEqual(nodes[1].config["image"], node_options_2["image"])
        self.assertEqual(nodes[1].config["size"], node_options_2["size"])

        self.assertEqual(nodes[2].name, node_options_3["name"])
        self.assertEqual(nodes[2].config["image"], node_options_3["image"])
        self.assertEqual(nodes[2].config["size"], node_options_3["size"])

        self.assertTrue(await pool.remove(nodes[0].id))
        self.assertTrue(await pool.remove(nodes[1].id))
        self.assertTrue(await pool.remove(nodes[2].id))
        self.assertEqual(len(await pool.items()), 0)
