import unittest
from libvirt_provider.instance.create import create
from libvirt_provider.instance.remove import remove
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
        success, response = await create(self.client, node_options)
        self.assertTrue(success)
        self.assertIn("instance", response)
        self.assertIsNotNone(response["instance"])
        node = response["instance"]
        self.assertIsInstance(node, Node)

        removed, remove_response = await remove(self.client, node.id)
        self.assertTrue(removed)

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

        success1, response1 = await create(self.client, **node_options_1)
        success2, response2 = await create(self.client, **node_options_2)
        success3, response3 = await create(self.client, **node_options_3)

        self.assertTrue(success1)
        self.assertIn("instance", response1)
        self.assertIsNotNone(response1["instance"])
        node1 = response1["instance"]

        self.assertEqual(node1.name, node_options_1["name"])
        self.assertEqual(node1.config["image"], node_options_1["image"])
        self.assertEqual(node1.config["size"], node_options_1["size"])

        self.assertTrue(success2)
        self.assertIn("instance", response2)
        self.assertIsNotNone(response2["instance"])
        node2 = response2["instance"]

        self.assertEqual(node2.name, node_options_2["name"])
        self.assertEqual(node2.config["image"], node_options_2["image"])
        self.assertEqual(node2.config["size"], node_options_2["size"])

        self.assertTrue(success3)
        self.assertIn("instance", response3)
        self.assertIsNotNone(response3["instance"])
        node3 = response3["instance"]

        self.assertEqual(node3.name, node_options_3["name"])
        self.assertEqual(node3.config["image"], node_options_3["image"])
        self.assertEqual(node3.config["size"], node_options_3["size"])

        removed1, remove_response1 = await remove(self.client, node1.id)
        self.assertTrue(removed1)

        removed2, remove_response2 = await remove(self.client, node2.id)
        self.assertTrue(removed2)

        removed3, remove_response3 = await remove(self.client, node3.id)
        self.assertTrue(removed3)


if __name__ == "__main__":
    unittest.main()
