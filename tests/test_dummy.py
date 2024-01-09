import unittest
from libvirt_provider.instance import create, remove
from libvirt_provider.defaults import DUMMY
from libvirt_provider.client import new_client
from libvirt_provider.models import Node
from libvirt_provider.pool import Pool
from libvirt_provider.utils.io import remove as remove_file


class TestDummy(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # The DummyDriver creates 2 nodes if creds is set to 0
        # If creds is set to -1, no nodes are created
        creds = -1
        self.client = new_client(DUMMY, creds)
        self.name = "dummy"

    async def tearDown(self):
        # Destroy all instances
        # Ensure that any pool is destroyed
        pool = Pool(self.name)
        for node in await pool.items():
            self.assertTrue(await remove(self.client, node.id))
        self.assertTrue(remove_file(self.name))

    async def test_create_dummy_node(self):
        # These options are ignored by the DummyDriver
        # But they must be given to the create method
        instance_options = {
            "name": "dummy-test",
            "image": "Ubuntu 9.10",
            "size": "Small",
        }
        instance = await create(self.client, instance_options)
        self.assertIsNotNone(instance)
        self.assertIsInstance(instance, Node)
        self.assertTrue(await remove(self.client, instance.id))

    async def test_dummy_nodes(self):
        # These options are ignored by the DummyDriver
        # But they must be given to the create method
        instance_options_1 = {
            "name": "dummy-test-1",
            "image": "Test Image",
            "size": "Small",
        }
        instance_options_2 = {
            "name": "dummy-test-2",
            "image": "Test Image",
            "size": "Medium",
        }
        instance_options_3 = {
            "name": "dummy-test-3",
            "image": "Test Image",
            "size": "Large",
        }

        instance1 = await create(self.client, instance_options_1)
        instance2 = await create(self.client, instance_options_2)
        instance3 = await create(self.client, instance_options_3)

        self.assertEqual(instance1.name, instance_options_1["name"])
        self.assertEqual(instance1.image, instance_options_1["image"])
        self.assertEqual(instance1.size, instance_options_1["size"])

        self.assertEqual(instance2.name, instance_options_2["name"])
        self.assertEqual(instance2.image, instance_options_2["image"])
        self.assertEqual(instance2.size, instance_options_2["size"])

        self.assertEqual(instance3.name, instance_options_3["name"])
        self.assertEqual(instance3.image, instance_options_3["image"])
        self.assertEqual(instance3.size, instance_options_3["size"])

        self.assertTrue(await remove(self.client, instance1.id))
        self.assertTrue(await remove(self.client, instance2.id))
        self.assertTrue(await remove(self.client, instance3.id))

    async def test_dummy_pool(self):
        db_name = "dummy"
        pool = Pool(db_name)
        self.assertIsNotNone(pool)
        self.assertEqual(pool.name, db_name)

        instance_options_1 = {
            "name": "dummy-test-1",
            "image": "Test Image",
            "size": "Small",
        }
        instance_options_2 = {
            "name": "dummy-test-2",
            "image": "Test Image",
            "size": "Medium",
        }
        instance_options_3 = {
            "name": "dummy-test-3",
            "image": "Test Image",
            "size": "Large",
        }

        self.assertTrue(
            await pool.add(await create(self.client, instance_options_1))
        )
        self.assertTrue(
            await pool.add(await create(self.client, instance_options_2))
        )
        self.assertTrue(
            await pool.add(await create(self.client, instance_options_3))
        )

        nodes = sorted(await pool.items(), key=lambda node: node.name)
        self.assertEqual(len(nodes), 3)

        for node in nodes:
            self.assertIsInstance(node, Node)

        self.assertEqual(nodes[0].name, instance_options_1["name"])
        self.assertEqual(nodes[0].image, instance_options_1["image"])
        self.assertEqual(nodes[0].size, instance_options_1["size"])

        self.assertEqual(nodes[1].name, instance_options_2["name"])
        self.assertEqual(nodes[1].image, instance_options_2["image"])
        self.assertEqual(nodes[1].size, instance_options_2["size"])

        self.assertEqual(nodes[2].name, instance_options_3["name"])
        self.assertEqual(nodes[2].image, instance_options_3["image"])
        self.assertEqual(nodes[2].size, instance_options_3["size"])

        self.assertTrue(await pool.remove(nodes[0].id))
        self.assertTrue(await pool.remove(nodes[1].id))
        self.assertTrue(await pool.remove(nodes[2].id))
        self.assertEqual(len(await pool.items()), 0)


if __name__ == "__main__":
    unittest.main()
