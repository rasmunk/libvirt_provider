import unittest
import os
import wget
from libvirt_provider.utils.io import remove as remove_file
from libvirt_provider.utils.io import copy, join, exists, makedirs, load_json
from libvirt_provider.defaults import LIBVIRT
from libvirt_provider.models import Node
from libvirt_provider.client import new_client
from libvirt_provider.instance import create, remove, stop, get, state


class TestLibvirt(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.architecture = "x86_64"
        self.name = f"libvirt-{self.architecture}"
        self.images_dir = join("tests", "images", self.architecture)
        if not exists(self.images_dir):
            self.assertTrue(makedirs(self.images_dir))

        self.image = join(self.images_dir, f"{self.name}-Rocky-9.qcow2")
        if not exists(self.image):
            # Download the image
            url = f"https://download.rockylinux.org/pub/rocky/9/images/{self.architecture}/Rocky-9-GenericCloud-Base.latest.{self.architecture}.qcow2"
            try:
                print(f"Downloading image: {url} for testing")
                wget.download(url, self.image)
            except Exception as err:
                print(f"Failed to download image: {url} - {err}")
                self.assertFalse(True)
        self.assertTrue(exists(self.image))

        open_uri = "qemu:///session"
        self.client = new_client(LIBVIRT, open_uri=open_uri)
        for i in range(4):
            test_image = join(self.images_dir, f"{self.name}-Rocky-9-{i}.qcow2")
            if not exists(test_image):
                self.assertTrue(copy(self.image, test_image))

    async def asyncTearDown(self):
        for i in range(4):
            test_image = join(self.images_dir, f"{self.name}-Rocky-9-{i}.qcow2")
            self.assertTrue(remove_file(test_image))
            self.assertFalse(exists(test_image))
        self.client.close()

    async def test_create_node(self):
        test_image = os.path.abspath(
            join(self.images_dir, f"{self.name}-Rocky-9-0.qcow2")
        )
        # Load architecture node_options
        node_options_path = join(
            "tests", "res", "node_options", f"{self.architecture}.json"
        )
        loaded_node_options = load_json(node_options_path)
        node_options = {
            "name": "test-1",
            "disk_image_path": test_image,
            "memory_size": "2048",
            **loaded_node_options,
        }
        node = await create(self.client, node_options)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, Node)
        self.assertTrue(await remove(self.client, node.id))

    async def test_stop_node(self):
        test_image = os.path.abspath(
            join(self.images_dir, f"{self.name}-Rocky-9-1.qcow2")
        )
        # Load architecture node_options
        node_options_path = join(
            "tests", "res", "node_options", f"{self.architecture}.json"
        )
        loaded_node_options = load_json(node_options_path)
        self.assertIsInstance(loaded_node_options, dict)
        node_options = {
            "name": "test-2",
            "disk_image_path": test_image,
            "memory_size": "2048",
            **loaded_node_options,
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

    async def test_create_node_with_xml_template(self):
        test_image = os.path.abspath(
            join(self.images_dir, f"{self.name}-Rocky-9-2.qcow2")
        )
        name = "test-3"
        node_options = {
            "name": name,
            "disk_image_path": test_image,
            "template_path": join("tests", "res", "templates", "libvirt.xml"),
        }
        node = await create(self.client, node_options)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, Node)
        self.assertTrue(await remove(self.client, node.id))


    async def test_create_node_with_jinja_template(self):
        test_image = os.path.abspath(
            join(self.images_dir, f"{self.name}-Rocky-9-3.qcow2")
        )
        name = "test-4"
        node_options = {
            "name": name,
            "template_path": join("tests", "res", "templates", "libvirt.j2"),
            "domain_type": "kvm",
            "disk_type": "file",
            "disk_driver_type": "qcow2",
            "disk_image_path": test_image,
            "disk_target_dev": "hda",
            "disk_target_bus": "ide",
            "memory_size": "1024",
            "num_vcpus": 1,
            "cpu_architecture": self.architecture,
            "machine": "pc",
            "serial_type": "pty",
            "serial_type_target_port": 0,
            "console_type": "pty",
        }
        node = await create(self.client, node_options)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, Node)
        self.assertTrue(await remove(self.client, node.id))


if __name__ == "__main__":
    unittest.main()
