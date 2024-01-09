import unittest
from libvirt_provider.defaults import LIBVIRT
from libvirt_provider.client import new_client
from libvirt_provider.instance import create, remove
from libvirt_provider.models import Node


class TestLibvirt(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        uri = "qemu:///system"
        driver_args = [uri]
        self.client = new_client(LIBVIRT, *driver_args)

    async def asyncTearDown(self):
        # Destroy all remaining instances
        # instances = await list_instances(self.client)
        # for instance in instances:
        #     await remove(self.client, instance.id)
        pass

    async def test_create_node(self):
        instance_options = {
            "domain": "test",
        }
        instance = await create(self.client, instance_options)
        self.assertIsNotNone(instance)
        self.assertIsInstance(instance, Node)
        self.assertTrue(await remove(self.client, instance.id))


if __name__ == "__main__":
    unittest.main()
