import unittest
import os
from libvirt_provider.defaults import LIBVIRT
from libvirt_provider.client import new_client
from libvirt_provider.models import Pool, Node
from libvirt_provider.instance import create, remove, get
from libvirt_provider.utils.io import remove as remove_file


class TestLibvirtPool(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.name = "libvirt-pool"
        open_uri = "qemu:///session"
        self.client = new_client(LIBVIRT, open_uri=open_uri)

    async def asyncTearDown(self):
        # Ensure that any pool is destroyed
        pool = Pool(self.name)
        for node in await pool.items():
            self.assertTrue(await remove(self.client, node.id))
        self.assertTrue(remove_file(self.name))
        self.client.close()

    async def test_libvirt_pool(self):
        db_name = "libvirt"
        pool = Pool(db_name)
        self.assertIsNotNone(pool)
        self.assertEqual(pool.name, db_name)

        node_options_1 = {
            "name": "libvirt-test-1",
            "disk_image_path": os.path.join(
                "iso", "Rocky-9-1.qcow2"
            ),
            "memory_size": "1024",
        }
        node_options_2 = {
            "name": "libvirt-test-2",
            "disk_image_path": os.path.join(
                "iso", "Rocky-9-2.qcow2"
            ),
            "memory_size": "2048",
        }
        node_options_3 = {
            "name": "libvirt-test-3",
            "disk_image_path": os.path.join(
                "iso", "Rocky-9-3.qcow2"
            ),
            "memory_size": "4096",
        }

        self.assertTrue(await pool.add(await create(self.client, node_options_1)))
        self.assertTrue(await pool.add(await create(self.client, node_options_2)))
        self.assertTrue(await pool.add(await create(self.client, node_options_3)))

        instance1 = await get(self.client, node_options_1["name"])
        instance2 = await get(self.client, node_options_2["name"])
        instance3 = await get(self.client, node_options_3["name"])

        self.assertEqual(instance1.name, node_options_1["name"])
        self.assertEqual(instance1.image, node_options_1["image"])
        self.assertEqual(instance1.size, node_options_1["size"])

        self.assertEqual(instance2.name, node_options_2["name"])
        self.assertEqual(instance2.image, node_options_2["image"])
        self.assertEqual(instance2.size, node_options_2["size"])

        self.assertEqual(instance3.name, node_options_3["name"])
        self.assertEqual(instance3.image, node_options_3["image"])
        self.assertEqual(instance3.size, node_options_3["size"])

        self.assertTrue(await remove(self.client, instance1.id))
        self.assertTrue(await remove(self.client, instance2.id))
        self.assertTrue(await remove(self.client, instance3.id))
