import unittest
from libvirt_provider.defaults import CONTAINER
from libvirt_provider.client import new_client


class TestContainer(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.name = "lxc"
        self.client = new_client(CONTAINER)

    async def asyncTearDown(self):
        self.client.close()
