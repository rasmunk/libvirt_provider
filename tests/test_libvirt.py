import unittest
import os
import wget
from libvirt_provider.utils.io import remove as remove_file
from libvirt_provider.utils.io import (
    copy,
    join,
    exists,
    makedirs,
    load_json,
    chown,
    chmod,
)
from libvirt_provider.utils.user import lookup_uid, lookup_gid
from libvirt_provider.defaults import LIBVIRT
from libvirt_provider.models import Node
from libvirt_provider.client import new_client
from libvirt_provider.instance.create import create
from libvirt_provider.instance.remove import remove
from libvirt_provider.instance.stop import stop
from libvirt_provider.instance.get import get
from libvirt_provider.instance.ls import ls
from libvirt_provider.instance.state import state


class TestLibvirt(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.user = "qemu"
        self.architecture = "x86_64"
        self.name = f"libvirt-{self.architecture}"
        # Note, a properly SELinux labelled directory is required when SELinux is enabled
        # self.images_dir = join(
        #    os.sep, "var", "lib", "libvirt", "images", self.architecture
        # )
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

        qemu_uid, qemu_gid = lookup_uid(self.user), lookup_gid(self.user)
        open_uri = "qemu:///session"
        self.client = new_client(LIBVIRT, open_uri=open_uri)
        for i in range(6):
            test_image = join(self.images_dir, f"{self.name}-Rocky-9-{i}.qcow2")
            if not exists(test_image):
                self.assertTrue(copy(self.image, test_image))
            self.assertTrue(exists(test_image))
            # Ensure correct ownership on image file
            self.assertTrue(chown(test_image, qemu_uid, qemu_gid))
            self.assertTrue(chmod(test_image, 0o755))

    async def asyncTearDown(self):
        for i in range(6):
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
        created, created_response = await create(self.client, **node_options)
        self.assertTrue(created)
        self.assertIn("instance", created_response)
        self.assertIsNotNone(created_response["instance"])
        node = created_response["instance"]

        self.assertIsNotNone(node)
        self.assertIsInstance(node, Node)
        removed, remove_response = await remove(self.client, node.id)
        self.assertTrue(removed)

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

        created, created_response = await create(self.client, **node_options)
        self.assertTrue(created)
        self.assertIn("instance", created_response)
        self.assertIsNotNone(created_response["instance"])
        new_node = created_response["instance"]

        self.assertIsNotNone(new_node)
        self.assertIsInstance(new_node, Node)

        get_success, get_response = await get(self.client, new_node.id)
        self.assertTrue(get_success)
        self.assertIn("instance", get_response)
        self.assertIsNotNone(get_response["instance"])
        node = get_response["instance"]

        self.assertIsNotNone(node)
        self.assertIsInstance(node, Node)
        self.assertEqual(node.id, new_node.id)
        stopped, stopped_response = await stop(self.client, node.id)
        self.assertTrue(stopped)

        state_success, state_response = await state(self.client, node.id)
        self.assertTrue(state_success)
        self.assertIn("state", state_response)
        self.assertIsNotNone(state_response["state"])
        node_state = state_response["state"]
        self.assertIsNot(node_state, False)
        # TODO, check that the state is actually running

        removed_success, remove_response = await remove(self.client, node.id)
        self.assertTrue(removed_success)

        get1_success, get1_response = await get(self.client, node.id)
        self.assertFalse(get1_success)

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
        create_success, create_response = await create(self.client, **node_options)
        self.assertTrue(create_success)
        self.assertIn("instance", create_response)
        self.assertIsNotNone(create_response["instance"])
        node = create_response["instance"]

        self.assertIsNotNone(node)
        self.assertIsInstance(node, Node)
        removed_success, remove_response = await remove(self.client, node.id)
        self.assertTrue(removed_success)

    async def test_create_node_with_jinja_template(self):
        test_image = os.path.abspath(
            join(self.images_dir, f"{self.name}-Rocky-9-3.qcow2")
        )
        name = "test-4"
        node_options = {
            "name": name,
            "template_path": join("tests", "res", "templates", "libvirt.j2"),
            "domain_type": "qemu",
            "disk_device_type": "file",
            "disk_driver_type": "qcow2",
            "disk_image_path": test_image,
            "disk_target_dev": "hda",
            "disk_target_bus": "ide",
            "memory_size": "1024MiB",
            "num_vcpus": 1,
            "cpu_architecture": self.architecture,
            "machine": "pc",
            "serial_type": "pty",
            "serial_type_target_port": 0,
            "console_type": "pty",
        }
        create_success, create_response = await create(self.client, **node_options)
        self.assertTrue(create_success)
        self.assertIn("instance", create_response)
        self.assertIsNotNone(create_response["instance"])
        node = create_response["instance"]
        self.assertIsNotNone(node)
        self.assertIsInstance(node, Node)

        removed_success, remove_response = await remove(self.client, node.id)
        self.assertTrue(removed_success)

    async def test_list_nodes(self):
        list_success, list_response = await ls(self.client)
        self.assertTrue(list_success)
        self.assertIn("instances", list_response)
        self.assertIsNotNone(list_response["instances"])
        nodes = list_response["instances"]

        self.assertIsNotNone(nodes)
        self.assertIsInstance(nodes, list)
        self.assertTrue(len(nodes) == 0)

        test_image_1 = os.path.abspath(
            join(self.images_dir, f"{self.name}-Rocky-9-4.qcow2")
        )
        node_options_1 = {
            "name": "test-5",
            "disk_image_path": test_image_1,
            "memory_size": "2048",
        }
        create_success1, create_response1 = await create(self.client, **node_options_1)
        self.assertTrue(create_success1)
        self.assertIn("instance", create_response1)
        self.assertIsNotNone(create_response1["instance"])
        node1 = create_response1["instance"]
        self.assertIsNotNone(node1)
        self.assertIsInstance(node1, Node)

        list_success1, list_response1 = await ls(self.client)
        self.assertTrue(list_success1)
        self.assertIn("instances", list_response1)
        self.assertIsNotNone(list_response1["instances"])
        nodes1 = list_response1["instances"]
        self.assertIsNotNone(nodes1)
        self.assertIsInstance(nodes1, list)
        self.assertTrue(len(nodes1) == 1)
        self.assertEqual(nodes1[0].id, node1.id)

        test_image_2 = os.path.abspath(
            join(self.images_dir, f"{self.name}-Rocky-9-5.qcow2")
        )

        node_options_2 = {
            "name": "test-6",
            "disk_image_path": test_image_2,
            "memory_size": "2048",
        }
        create_success2, create_response2 = await create(self.client, **node_options_2)
        self.assertTrue(create_success2)
        self.assertIn("instance", create_response2)
        self.assertIsNotNone(create_response2["instance"])
        node2 = create_response2["instance"]
        self.assertIsNotNone(node2)
        self.assertIsInstance(node2, Node)

        list_success2, list_response2 = await ls(self.client)
        self.assertTrue(list_response2)
        self.assertIn("instances", list_response2)
        self.assertIsNotNone(list_response2["instances"])
        nodes2 = list_response2["instances"]

        self.assertIsNotNone(nodes2)
        self.assertIsInstance(nodes2, list)
        self.assertTrue(len(nodes2) == 2)

        for node in nodes2:
            removed_success, response = await remove(self.client, node.id)
            self.assertTrue(removed_success)

        list_success3, list_response3 = await ls(self.client)
        self.assertTrue(list_response3)
        self.assertIn("instances", list_response3)
        self.assertIsNotNone(list_response3["instances"])
        nodes3 = list_response3["instances"]
        self.assertIsNotNone(nodes3)
        self.assertIsInstance(nodes3, list)
        self.assertTrue(len(nodes3) == 0)


if __name__ == "__main__":
    unittest.main()
