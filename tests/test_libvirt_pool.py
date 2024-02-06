import unittest
import os
import wget
from libvirt_provider.utils.io import remove as remove_file
from libvirt_provider.utils.io import copy, exists, join, makedirs, load_json
from libvirt_provider.defaults import LIBVIRT
from libvirt_provider.client import new_client
from libvirt_provider.pool import Pool
from libvirt_provider.models import Node
from libvirt_provider.instance import create, remove


class TestLibvirtPool(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.architecture = "x86_64"
        self.name = f"libvirt-pool-{self.architecture}"
        self.images_dir = join("tests", "images", self.architecture)
        if not exists(self.images_dir):
            self.assertTrue(makedirs(self.images_dir))

        self.image = join(self.images_dir, f"{self.name}-Rocky-9.qcow2")
        if not exists(self.image):
            # Download the image
            url = f"https://download.rockylinux.org/pub/rocky/9/images/{self.architecture}/Rocky-9-GenericCloud-Base.latest.{self.architecture}.qcow2"
            try:
                print(f"Downloading image: {url} for testing")
                wget.download(url, self.image)
            except Exception as err:
                print(f"Failed to download image: {url} - {err}")
                self.assertFalse(True)
        self.assertTrue(exists(self.image))

        for i in range(2):
            test_image = join(self.images_dir, f"{self.name}-Rocky-9-{i}.qcow2")
            self.assertTrue(copy(self.image, test_image))
            self.assertTrue(exists(test_image))

        open_uri = "qemu:///session"
        self.client = new_client(LIBVIRT, open_uri=open_uri)

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
            test_image = join(self.images_dir, f"{self.name}-Rocky-9-{i}.qcow2")
            self.assertTrue(remove_file(test_image))
            self.assertFalse(exists(test_image))

    async def test_libvirt_pool(self):
        for i in range(2):
            test_image = os.path.abspath(join(self.images_dir, f"Rocky-9-{i}.qcow2"))
            self.assertTrue(copy(self.image, test_image))
            self.assertTrue(exists(test_image))

            # Load architecture node_options
            node_options_path = join(
                "tests", "res", "node_options", f"{self.architecture}.json"
            )
            loaded_node_options = load_json(node_options_path)
            self.assertIsInstance(loaded_node_options, dict)

            pool = Pool(self.name)
            self.assertIsNotNone(pool)
            self.assertEqual(pool.name, self.name)
            self.assertEqual(len(await pool.items()), 0)

            node_options = {
                "name": f"libvirt-test-{i}",
                "disk_image_path": test_image,
                "memory_size": "4096",
                **loaded_node_options,
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
