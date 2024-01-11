import unittest
import os
from libvirt_provider.utils.io import remove as remove_file
from libvirt_provider.utils.io import copy, exists, join
from libvirt_provider.defaults import LIBVIRT
from libvirt_provider.client import new_client
from libvirt_provider.pool import Pool
from libvirt_provider.models import Node
from libvirt_provider.instance import create, remove


class TestLibvirtPool(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.name = "libvirt-pool"
        self.base_image = join("tests", "images", "Rocky-9.qcow2")
        self.assertTrue(os.path.exists(self.base_image))

        open_uri = "qemu:///session"
        self.client = new_client(LIBVIRT, open_uri=open_uri)

        for i in range(2):
            test_image = join("tests", "images", "Rocky-9-{}.qcow2".format(i))
            self.assertTrue(copy(self.base_image, test_image))
            self.assertTrue(exists(test_image))

    async def asyncTearDown(self):
        # Ensure that any pool is destroyed
        pool = Pool(self.name)
        for node in await pool.items():
            self.assertTrue(await remove(self.client, node.id))
        self.assertTrue(await pool.flush())
        self.assertEqual(len(await pool.items()), 0)
        self.assertTrue(await pool.remove_persistence())
        self.client.close()

        for i in range(2):
            test_image = join("tests", "images", "Rocky-9-{}.qcow2".format(i))
            self.assertTrue(remove_file(test_image))
            self.assertFalse(exists(test_image))

    async def test_libvirt_pool(self):
        for i in range(2):
            test_image = os.path.abspath(
                join("tests", "images", "Rocky-9-{}.qcow2".format(i))
            )

            self.assertTrue(copy(self.base_image, test_image))
            self.assertTrue(exists(test_image))

            pool = Pool(self.name)
            self.assertIsNotNone(pool)
            self.assertEqual(pool.name, self.name)
            self.assertEqual(len(await pool.items()), 0)

            node_options = {
                "name": "libvirt-test-{}".format(i),
                "disk_image_path": test_image,
                "memory_size": "4096",
            }

            node = await create(self.client, node_options)
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

            self.assertTrue(await remove(self.client, node.id))
