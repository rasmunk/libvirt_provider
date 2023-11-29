import unittest
from libcloud.compute.base import Node
from libvirt_provider.instance import create, destroy
from libvirt_provider.defaults import default_driver_config, DUMMY
from libvirt_provider.helpers import new_apache_client


class TestDummy(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

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


if __name__ == "__main__":
    unittest.main()
