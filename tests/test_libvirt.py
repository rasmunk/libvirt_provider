import unittest
import os
from libvirt import virDomain
from libvirt_provider.defaults import LIBVIRT
from libvirt_provider.client import new_client
from libvirt_provider.instance import create, remove, stop, get, state


class TestLibvirt(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        open_uri = "qemu:///session"
        self.client = new_client(LIBVIRT, open_uri=open_uri)

    async def asyncTearDown(self):
        self.client.close()

    async def test_create_node(self):
        node_options = {
            "name": "test-1",
            "disk_image_path": os.path.join(
                "iso",
                "Rocky-9-1.qcow2"
            ),
            "memory_size": "1024",
        }

        node_id = await create(self.client, node_options)
        self.assertIsNotNone(node_id)
        self.assertIsInstance(node_id, str)
        self.assertTrue(await remove(self.client, node_id))

    async def test_stop_node(self):
        node_options = {
            "name": "test-2",
            "disk_image_path": os.path.join(
                "iso"
                "Rocky-9-1.qcow2",
            ),
            "memory_size": "2048",
        }

        node_id = await create(self.client, node_options)
        self.assertIsNotNone(node_id)
        self.assertIsInstance(node_id, str)

        node = await get(self.client, node_id)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, virDomain)
        self.assertEqual(node_id, node.UUIDString())

        self.assertTrue(await stop(self.client, node_id))

        node_state = await state(self.client, node_id)
        self.assertIsNot(node_state, False)
        # TODO, check that the state is actually running

        self.assertTrue(await remove(self.client, node_id))

        node = await get(self.client, node_id)
        self.assertFalse(node)


if __name__ == "__main__":
    unittest.main()
