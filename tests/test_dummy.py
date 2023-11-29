import unittest
from libcloud.compute.base import Node
from libvirt_provider.instance import create, destroy, list_instances
from libvirt_provider.defaults import default_driver_config, DUMMY
from libvirt_provider.helpers import new_apache_client


class TestDummy(unittest.TestCase):
    def setUp(self):
        # The DummyDriver creates 2 nodes if creds is set to 0
        # If creds is set to -1, no nodes are created
        creds = -1
        self.client = new_apache_client(DUMMY, creds)

    def tearDown(self):
        # Destroy all remaining instances
        instances = list_instances(self.client)
        for instance in instances:
            destroy(self.client, instance.id)

    def test_create_dummy_node(self):
        # These options are ignored by the DummyDriver
        # But they must be given to the create method
        instance_options = {
            "name": "dummy-test",
            "image": "Ubuntu 9.10",
            "size": "Small",
        }
        instance = create(self.client, instance_options)
        self.assertIsNotNone(instance)
        self.assertIsInstance(instance, Node)
        self.assertTrue(destroy(self.client, instance.id))

    def test_list_dummy_nodes(self):
        # Validate that there are no other instances
        instances = list_instances(self.client)
        self.assertEqual(len(instances), 0)

        # These options are ignored by the DummyDriver
        # But they must be given to the create method
        instance_options = {
            "name": "",
            "image": "",
            "size": "Small",
        }

        instance1 = create(self.client, instance_options)
        instance2 = create(self.client, instance_options)
        instance3 = create(self.client, instance_options)

        instances = list_instances(self.client)
        self.assertIsNotNone(instances)
        self.assertIsInstance(instances, list)

        self.assertEqual(instances[0].id, instance1.id)
        self.assertEqual(instances[1].id, instance2.id)
        self.assertEqual(instances[2].id, instance3.id)

        self.assertTrue(destroy(self.client, instance1.id))
        self.assertTrue(destroy(self.client, instance2.id))
        self.assertTrue(destroy(self.client, instance3.id))

    def test_destroy_dummy_nodes(self):
        # These options are ignored by the DummyDriver
        # But they must be given to the create method
        instance_options = {
            "name": "",
            "image": "",
            "size": "Small",
        }
        instance1 = create(self.client, instance_options)
        self.assertIsNotNone(instance1)
        self.assertIsInstance(instance1, Node)
        self.assertEqual(instance1.name, "dummy-1")
        self.assertEqual(len(list_instances(self.client)), 1)

        self.assertTrue(destroy(self.client, instance1.id))
        self.assertEqual(len(list_instances(self.client)), 0)

        instance2 = create(self.client, instance_options)
        self.assertIsNotNone(instance2)
        self.assertIsInstance(instance2, Node)
        self.assertEqual(instance2.name, "dummy-1")
        self.assertEqual(len(list_instances(self.client)), 1)

        self.assertTrue(destroy(self.client, instance2.id))
        self.assertEqual(len(list_instances(self.client)), 0)


if __name__ == "__main__":
    unittest.main()
