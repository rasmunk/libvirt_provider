import unittest
import os
from libvirt_provider.utils.io import remove as remove_file
from libvirt_provider.utils.io import copy, join
from libvirt_provider.defaults import LIBVIRT
from libvirt_provider.models import Node
from libvirt_provider.client import new_client
from libvirt_provider.instance import create, remove, stop, get, state


class TestLibvirt(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.base_image = join("tests", "images", "Rocky-9.qcow2")
        self.assertTrue(os.path.exists(self.base_image))

        open_uri = "qemu:///session"
        self.client = new_client(LIBVIRT, open_uri=open_uri)

        for i in range(2):
            test_image = join("tests", "images", "Rocky-9-{}.qcow2".format(i))
            self.assertTrue(copy(self.base_image, test_image))
            self.assertTrue(os.path.exists(test_image))

    async def asyncTearDown(self):
        self.client.close()

        for i in range(2):
            test_image = join("tests", "images", "Rocky-9-{}.qcow2".format(i))
            self.assertTrue(remove_file(test_image))
            self.assertFalse(os.path.exists(test_image))

    async def test_create_node(self):
        test_image = os.path.abspath(join("tests", "images", "Rocky-9-0.qcow2"))
        node_options = {
            "name": "test-1",
            "disk_image_path": test_image,
            "memory_size": "2048",
        }
        node = await create(self.client, node_options)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, Node)
        self.assertTrue(await remove(self.client, node.id))

    async def test_stop_node(self):
        test_image = os.path.abspath(join("tests", "images", "Rocky-9-1.qcow2"))
        node_options = {
            "name": "test-2",
            "disk_image_path": test_image,
            "memory_size": "2048",
        }

        new_node = await create(self.client, node_options)
        self.assertIsNotNone(new_node)
        self.assertIsInstance(new_node, Node)

        node = await get(self.client, new_node.id)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, Node)
        self.assertEqual(node.id, new_node.id)
        self.assertTrue(await stop(self.client, node.id))

        node_state = await state(self.client, node.id)
        self.assertIsNot(node_state, False)
        # TODO, check that the state is actually running
        self.assertTrue(await remove(self.client, node.id))
        node = await get(self.client, node.id)
        self.assertFalse(node)


if __name__ == "__main__":
    unittest.main()
