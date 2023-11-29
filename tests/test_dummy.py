import unittest
from libcloud.compute.base import Node
from libvirt_provider.instance import create, destroy, list_instances
from libvirt_provider.defaults import default_driver_config, DUMMY
from libvirt_provider.helpers import new_apache_client


class TestDummy(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        creds = 0
        client = new_apache_client(DUMMY, creds)
        # Destroy all remaining instances
        instances = list_instances(client)
        for instance in instances:
            destroy(client, instance.id)

    def test_create_dummy_node(self):
        creds = 0
        client = new_apache_client(DUMMY, creds)
        images = client.list_images()
        sizes = client.list_sizes()
        # These options are ignored by the DummyDriver
        # But they must be given to the create method
        instance_options = {
            "name": "dummy-test",
            "image": "Ubuntu 9.10",
            "size": "Small",
        }
        instance = create(client, instance_options)
        self.assertIsNotNone(instance)
        self.assertIsInstance(instance, Node)
        self.assertTrue(destroy(client, instance.id))

    def test_list_dummy_nodes(self):
        creds = 0
        client = new_apache_client(DUMMY, creds)
        # Validate that there are no other instances
        self.assertEqual(len(list_instances(client)), 0)

        # These options are ignored by the DummyDriver
        # But they must be given to the create method
        instance_options = {
            "name": "",
            "image": "",
            "size": "",
        }
        instance1 = create(client, instance_options)
        instance2 = create(client, instance_options)
        instance3 = create(client, instance_options)

        instances = list_instances(client)
        self.assertIsNotNone(instances)
        self.assertLen(instances, 3)

        self.assertIsEqual(instances[0].id, instance1.id)
        self.assertIsEqual(instances[1].id, instance2.id)
        self.assertIsEqual(instances[2].id, instance3.id)

        self.assertIsNotNone(instances)
        self.assertIsInstance(instances, list)
        self.assertTrue(destroy(client, instance.id))


if __name__ == "__main__":
    unittest.main()
