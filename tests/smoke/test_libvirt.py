# Copyright (C) 2024  rasmunk
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import unittest
import pytest
import os
import random
from libvirt_provider.utils.io import (
    copy,
    join,
    exists,
    load_json,
)
from libvirt_provider.defaults import LIBVIRT
from libvirt_provider.models import Node
from libvirt_provider.client import new_client
from libvirt_provider.instance.create import create
from libvirt_provider.instance.remove import remove
from libvirt_provider.instance.stop import stop
from libvirt_provider.instance.get import get
from libvirt_provider.instance.ls import ls
from libvirt_provider.instance.start import start
from libvirt_provider.instance.state import state
from tests.context import LibvirtTestContext, CPU_ARCHITECTURE


@pytest.mark.smoke
class TestLibvirt(unittest.IsolatedAsyncioTestCase):
    context = LibvirtTestContext()

    async def asyncSetUp(self):
        await self.context.setUp()

        self.seed = str(random.random())[2:10]
        context_image_split = self.context.image.split(".")
        new_test_image = "{}-{}.{}".format(
            context_image_split[0], self.seed, context_image_split[-1]
        )

        self.test_image = os.path.realpath(new_test_image)
        self.assertTrue(copy(self.context.image, self.test_image))
        self.assertTrue(exists(self.test_image))
        open_uri = "qemu:///session"
        self.client = new_client(LIBVIRT, open_uri=open_uri)

    async def asyncTearDown(self):
        # Cleanup the started nodes
        search_regex = f".*test-{self.seed}.*"
        found, test_nodes = await ls(self.client, regex=search_regex)
        for node in test_nodes["instances"]:
            stopped, result = await stop(self.client, node.id)
            self.assertTrue(stopped)

        self.assertTrue(found)
        for node in test_nodes["instances"]:
            removed, result = await remove(self.client, node.id)
            self.assertTrue(removed)

        found, test_nodes = await ls(self.client, regex=search_regex)
        self.assertTrue(found)
        self.assertTrue(len(test_nodes["instances"]) == 0)
        self.client.close()

    @classmethod
    def tearDownClass(cls):
        cls.context.tearDown()

    async def test_create_node(self):
        test_name = f"create-test-{self.seed}"
        loaded_node_options = load_json(self.context.node_options_path)
        node_options = {
            "name": test_name,
            "disk_image_path": self.test_image,
            "memory_size": "1024MiB",
            **loaded_node_options,
        }
        created, created_response = await create(self.client, **node_options)
        self.assertTrue(created)
        self.assertIn("instance", created_response)
        self.assertIsNotNone(created_response["instance"])
        node = created_response["instance"]

        # Check that the node is created and not started
        state_success, state_response = await state(self.client, node.id)
        self.assertTrue(state_success)
        self.assertIn("state", state_response)
        self.assertIsNotNone(state_response["state"])
        node_state = state_response["state"]
        self.assertIsNot(node_state, False)
        self.assertEqual(node_state, "shut off")

        # Remove the node
        removed, remove_response = await remove(self.client, node.id)
        self.assertTrue(removed)

    async def test_start_node(self):
        test_name = f"start-test-{self.seed}"
        # Load architecture node_options
        loaded_node_options = load_json(self.context.node_options_path)
        self.assertIsInstance(loaded_node_options, dict)
        node_options = {
            "name": test_name,
            "disk_image_path": self.test_image,
            "memory_size": "1024MiB",
            **loaded_node_options,
        }

        created, created_response = await create(self.client, **node_options)
        self.assertTrue(created)
        self.assertIn("instance", created_response)
        self.assertIsNotNone(created_response["instance"])
        new_node = created_response["instance"]
        self.assertIsNotNone(new_node)
        self.assertIsInstance(new_node, Node)

        state_success, state_response = await state(self.client, new_node.id)
        self.assertTrue(state_success)
        self.assertIn("state", state_response)
        self.assertIsNotNone(state_response["state"])
        node_state = state_response["state"]
        self.assertIsNot(node_state, False)
        self.assertEqual(node_state, "shut off")

        started, started_response = await start(self.client, new_node.id)
        self.assertTrue(started)

        state_success, state_response = await state(self.client, new_node.id)
        self.assertTrue(state_success)
        self.assertIn("state", state_response)
        self.assertIsNotNone(state_response["state"])
        node_state = state_response["state"]
        self.assertIsNot(node_state, False)
        self.assertEqual(node_state, "running")

    async def test_stop_node(self):
        test_name = f"stop-test-{self.seed}"
        # Load architecture node_options
        loaded_node_options = load_json(self.context.node_options_path)
        self.assertIsInstance(loaded_node_options, dict)
        node_options = {
            "name": test_name,
            "disk_image_path": self.test_image,
            "memory_size": "1024MiB",
            **loaded_node_options,
        }

        created, created_response = await create(self.client, **node_options)
        self.assertTrue(created)
        self.assertIn("instance", created_response)
        self.assertIsNotNone(created_response["instance"])
        new_node = created_response["instance"]
        self.assertIsNotNone(new_node)
        self.assertIsInstance(new_node, Node)

        started, started_response = await start(self.client, new_node.id)
        self.assertTrue(started)

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
        self.assertEqual(node_state, "shut off")

        removed_success, remove_response = await remove(self.client, node.id)
        self.assertTrue(removed_success)

        get1_success, get1_response = await get(self.client, node.id)
        self.assertFalse(get1_success)

    async def test_create_node_with_xml_template(self):
        test_name = f"create-xml-test-{self.seed}"
        node_options = {
            "name": test_name,
            "disk_image_path": self.test_image,
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
        test_name = f"create-jinja-test-{self.seed}"
        if CPU_ARCHITECTURE == "aarch64":
            machine = "virt"
            # https://bugs.launchpad.net/nova/+bug/1864588
            cpu_mode = "custom"
            disk_target_dev = "vda"
            disk_target_bus = "virtio"
        else:
            machine = "pc"
            cpu_mode = "host-model"
            disk_target_dev = "hda"
            disk_target_bus = "ide"

        node_options = {
            "name": test_name,
            "template_path": join("tests", "res", "templates", "libvirt.j2"),
            "domain_type": "qemu",
            "disk_device_type": "file",
            "disk_driver_name": "qemu",
            "disk_driver_type": "qcow2",
            "disk_image_path": self.test_image,
            "disk_target_dev": disk_target_dev,
            "disk_target_bus": disk_target_bus,
            "memory_size": "1024MiB",
            "num_vcpus": 1,
            "cpu_architecture": self.context.architecture,
            "cpu_mode": cpu_mode,
            "machine": machine,
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
        test_name = f"list-test-{self.seed}"
        search_regex = f".*{test_name}.*"
        list_success, list_response = await ls(self.client, regex=search_regex)
        self.assertTrue(list_success)
        self.assertIn("instances", list_response)
        self.assertIsNotNone(list_response["instances"])
        nodes = list_response["instances"]

        self.assertIsNotNone(nodes)
        self.assertIsInstance(nodes, list)
        self.assertTrue(len(nodes) == 0)

        node_options_1 = {
            "name": f"{test_name}-1",
            "disk_image_path": self.test_image,
            "memory_size": "1024MiB",
        }
        create_success1, create_response1 = await create(self.client, **node_options_1)
        self.assertTrue(create_success1)
        self.assertIn("instance", create_response1)
        self.assertIsNotNone(create_response1["instance"])
        node1 = create_response1["instance"]
        self.assertIsNotNone(node1)
        self.assertIsInstance(node1, Node)

        list_success1, list_response1 = await ls(self.client, regex=search_regex)
        self.assertTrue(list_success1)
        self.assertIn("instances", list_response1)
        self.assertIsNotNone(list_response1["instances"])
        nodes1 = list_response1["instances"]
        self.assertIsNotNone(nodes1)
        self.assertIsInstance(nodes1, list)
        self.assertTrue(len(nodes1) == 1)
        self.assertEqual(nodes1[0].id, node1.id)

        node_options_2 = {
            "name": f"{test_name}-2",
            "disk_image_path": self.test_image,
            "memory_size": "1024MiB",
        }
        create_success2, create_response2 = await create(self.client, **node_options_2)
        self.assertTrue(create_success2)
        self.assertIn("instance", create_response2)
        self.assertIsNotNone(create_response2["instance"])
        node2 = create_response2["instance"]
        self.assertIsNotNone(node2)
        self.assertIsInstance(node2, Node)

        list_success2, list_response2 = await ls(self.client, regex=search_regex)
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

        list_success3, list_response3 = await ls(self.client, regex=search_regex)
        self.assertTrue(list_response3)
        self.assertIn("instances", list_response3)
        self.assertIsNotNone(list_response3["instances"])
        nodes3 = list_response3["instances"]
        self.assertIsNotNone(nodes3)
        self.assertIsInstance(nodes3, list)
        self.assertTrue(len(nodes3) == 0)


if __name__ == "__main__":
    unittest.main()
