import unittest
from libvirt_provider.instance import create, remove
from libvirt_provider.defaults import DUMMY
from libvirt_provider.client import new_client
from libvirt_provider.models import Node


class TestDummy(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.name = "dummy"
        self.client = new_client(DUMMY)

    async def asyncTearDown(self):
        # Destroy all instances
        pass

    async def test_create_dummy_node(self):
        # These options are ignored by the DummyDriver
        # But they must be given to the create method
        node_options = {
            "name": "dummy-test",
            "image": "Ubuntu 9.10",
            "size": "Small",
        }
        node = await create(self.client, node_options)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, Node)
        self.assertTrue(await remove(self.client, node.id))

    async def test_dummy_nodes(self):
        # These options are ignored by the DummyDriver
        # But they must be given to the create method
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

        node1 = await create(self.client, node_options_1)
        node2 = await create(self.client, node_options_2)
        node3 = await create(self.client, node_options_3)

        self.assertEqual(node1.name, node_options_1["name"])
        self.assertEqual(node1.config["image"], node_options_1["image"])
        self.assertEqual(node1.config["size"], node_options_1["size"])

        self.assertEqual(node2.name, node_options_2["name"])
        self.assertEqual(node2.config["image"], node_options_2["image"])
        self.assertEqual(node2.config["size"], node_options_2["size"])

        self.assertEqual(node3.name, node_options_3["name"])
        self.assertEqual(node3.config["image"], node_options_3["image"])
        self.assertEqual(node3.config["size"], node_options_3["size"])

        self.assertTrue(await remove(self.client, node1.id))
        self.assertTrue(await remove(self.client, node2.id))
        self.assertTrue(await remove(self.client, node3.id))


if __name__ == "__main__":
    unittest.main()
