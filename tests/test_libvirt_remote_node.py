import unittest
import os
import wget
from libvirt_provider.utils.io import remove as remove_file
from libvirt_provider.utils.io import copy, join, makedirs, exists, hashsum
from libvirt_provider.defaults import LIBVIRT
from libvirt_provider.models import Node
from libvirt_provider.client import new_client
from libvirt_provider.instance import create, remove, stop, get, state
from deling.io.datastores.core import SFTPStore
from deling.authenticators.ssh import SSHAuthenticator

class TestLibvirtRemote(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.name = "libvirt-remote"
        images_dir = join("tests", "images")
        if not exists(images_dir):
            self.assertTrue(makedirs(images_dir))

        self.image = join(images_dir, "Rocky-9.qcow2")
        if not exists(self.image):
            # Download the image
            url = "https://download.rockylinux.org/pub/rocky/9/images/x86_64/Rocky-9-GenericCloud-Base.latest.x86_64.qcow2"
            try:
                print("Downloading image: {} for testing".format(url))
                wget.download(url, self.image)
            except Exception as err:
                print("Failed to download image: {} - {}".format(url, err))
                self.assertFalse(True)
        self.assertTrue(exists(self.image))

        username = os.environ.get("LIBVIRT_REMOTE_USERNAME", "mountuser")
        password = os.environ.get("LIBVIRT_REMOTE_PASSWORD", "Passw0rd!")
        private_key_file = os.environ.get("LIBVIRT_REMOTE_PRIVATE_KEY_FILE", None)
        hostname = os.environ.get("LIBVIRT_REMOTE_HOSTNAME", "127.0.0.1")
        port = os.environ.get("LIBVIRT_REMOTE_PORT", 2222)

        self.datastore = SFTPStore(
            host=hostname,
            port=port,
            authenticator=SSHAuthenticator(
                username=username,
                password=password,
                private_key_file=private_key_file
            ),
        )
        self.assertTrue(self.datastore.mkdir(images_dir, recursive=True))
        self.assertTrue(self.datastore.upload(self.image, self.image))

        remote_uri = f"qemu+ssh://{username}@{hostname}/session"
        self.client = new_client(LIBVIRT, open_uri=remote_uri)
        for i in range(2):
            test_image = join(
                "tests", "images", "{}-Rocky-9-{}.qcow2".format(self.name, i)
            )
            self.assertTrue(copy(self.base_image, test_image))
            self.assertTrue(os.path.exists(test_image))

    async def asyncTearDown(self):
        for i in range(2):
            test_image = join(
                "tests", "images", "{}-Rocky-9-{}.qcow2".format(self.name, i)
            )
            self.assertTrue(remove_file(test_image))
            self.assertFalse(os.path.exists(test_image))
        self.client.close()

    async def test_create_node(self):
        test_image = os.path.abspath(
            join("tests", "images", "{}-Rocky-9-0.qcow2".format(self.name))
        )
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
