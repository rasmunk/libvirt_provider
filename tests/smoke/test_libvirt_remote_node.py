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
from libvirt_provider.utils.io import (
    join,
    makedirs,
    exists,
    load_json,
    get_gid,
    chown,
    chmod,
    access,
)
from libvirt_provider.defaults import LIBVIRT
from libvirt_provider.models import Node
from libvirt_provider.client import new_client
from libvirt_provider.instance.create import create
from libvirt_provider.instance.remove import remove
from libvirt_provider.instance.stop import stop
from libvirt_provider.instance.get import get
from libvirt_provider.instance.state import state
from libvirt_provider.utils.user import (
    lookup_gid,
    find_user_with_username,
    find_group_with_groupname,
)
from deling.io.datastores.core import SFTPStore
from deling.authenticators.ssh import SSHAuthenticator
from .utils.job import run

current_dir = os.path.abspath(os.path.dirname(__file__))


class LibvirtSetupContext:
    def __init__(self):
        self.init_done = False

    async def setUp(self):
        if self.init_done:
            return

        user_base = "qemu"
        self.user = find_user_with_username(user_base)
        assert self.user
        self.group = find_group_with_groupname(user_base)
        assert self.group

        self.architecture = "x86_64"
        self.name = f"host-vm-for-remote-test-{self.architecture}"

        # Start a dummy VM, that can be used
        # to test the remote libvirt node.
        # Download and configure the test image
        self.images_dir = join(current_dir, "images", self.architecture)
        if not exists(self.images_dir):
            assert makedirs(self.images_dir)
        self.base_image = join(self.images_dir, f"{self.name}-base.qcow2")
        gen_vm_dir = join(current_dir, "res", "gen-vm-image")
        if not exists(self.base_image):
            gen_vm_architecture = join(gen_vm_dir, "architecture.yml")
            gen_vm_command = [
                "gen-vm-image",
                "--architecture-path",
                gen_vm_architecture,
                "--image-output-path",
                self.base_image,
            ]
            result = run(gen_vm_command)
            assert result["returncode"] == 0

        # Configure the VM image
        self.image = join(self.images_dir, f"{self.name}-configured.qcow2")
        if not exists(self.image):
            cloud_init_config_path = join(gen_vm_dir, "cloud-init-config")
            meta_data_path = join(cloud_init_config_path, "meta-data")
            user_data_path = join(cloud_init_config_path, "user-data")
            vendor_data_path = join(cloud_init_config_path, "vendor-data")
            configure_vm_command = [
                "configure-vm-image",
                "--image-input-path",
                self.image,
                "--config-user-data-path",
                user_data_path,
                "--config-meta-data-path",
                meta_data_path,
                "--config-vendor-data-path",
                vendor_data_path,
            ]
            result = run(configure_vm_command)
            assert result["returncode"] == 0

        qemu_gid = lookup_gid(self.group)
        assert qemu_gid

        # Ensure that correct permissions are set on the image file
        existing_gid = get_gid(self.image)
        assert existing_gid

        if not access(self.image, os.R_OK | os.X_OK):
            assert chmod(self.image, 0o755)
        assert access(self.image, os.R_OK | os.X_OK)

        if existing_gid != qemu_gid:
            assert chown(self.image, gid=qemu_gid)

        node_options_path = join(current_dir, "res", "node_options", "x86_64.json")
        loaded_node_options = load_json(node_options_path)
        node_options = {
            "name": "remote-test-vm",
            "disk_image_path": self.image,
            "memory_size": "2048MiB",
            "cpu_architecture": self.architecture,
            **loaded_node_options,
        }

        open_uri = "qemu:///session"
        self.client = new_client(LIBVIRT, open_uri=open_uri)
        self.vm_created, response = await create(self.client, **node_options)
        assert self.vm_created
        assert "instance" in response
        assert response["instance"] is not None
        self.vm = response["instance"]
        self.init_done = True

    async def tearDown(self):
        # Remove VM
        if self.init_done:
            removed, removed_response = await remove(self.client, self.vm.id)
            assert removed
            self.init_done = False
        if exists(self.image):
            assert remove(self.image)


@pytest.mark.smoke
class TestLibvirtRemote(unittest.IsolatedAsyncioTestCase):
    context = LibvirtSetupContext()

    async def asyncSetUp(self):
        await self.context.setUp()
        self.remote_user = "qemu"
        self.architecture = "x86_64"
        self.name = f"libvirt-remote-{self.architecture}"

        username = os.environ.get("LIBVIRT_REMOTE_USERNAME", "mountuser")
        password = os.environ.get("LIBVIRT_REMOTE_PASSWORD", "Passw0rd!")
        hostname = os.environ.get("LIBVIRT_REMOTE_HOSTNAME", "127.0.0.1")
        port = os.environ.get("LIBVIRT_REMOTE_PORT", 2222)
        self.datastore = SFTPStore(
            host=hostname,
            port=port,
            authenticator=SSHAuthenticator(username=username, password=password),
        )

        self.assertTrue(self.datastore.mkdir(self.images_dir, recursive=True))
        if not self.datastore.exists(self.image):
            self.assertTrue(self.datastore.upload(self.image, self.image))
        # TODO, lookup the remote node uid/gid for the self.libvirt_user
        remote_qemu_uid, remote_qemu_gid = 107, 107
        for i in range(2):
            test_image = join(self.images_dir, f"{self.name}-Rocky-9-{i}.qcow2")
            if not self.datastore.exists(test_image):
                self.assertTrue(self.datastore.copy(self.image, test_image))
            self.assertTrue(self.datastore.exists(test_image))
            test_image_stats = self.datastore.stat(test_image)
            self.assertNotEqual(test_image_stats, False)
            test_image_stats.uid = remote_qemu_uid
            test_image_stats.gid = remote_qemu_gid
            self.assertTrue(self.datastore.setstat(test_image, test_image_stats))

        remote_uri = f"qemu+ssh://{username}@{hostname}/session"
        self.client = new_client(LIBVIRT, open_uri=remote_uri)

    async def asyncTearDown(self):
        await self.context.tearDown()
        for i in range(2):
            test_image = join(self.images_dir, f"{self.name}-Rocky-9-{i}.qcow2")
            self.assertTrue(self.datastore.remove(test_image))
            self.assertFalse(self.datastore.exists(test_image))
        self.client.close()

    async def test_create_node(self):
        test_image = self.datastore.realpath(
            join(self.images_dir, f"{self.name}-Rocky-9-0.qcow2")
        )
        # Load architecture node_options
        node_options_path = join("res", "node_options", f"{self.architecture}.json")
        loaded_node_options = load_json(node_options_path)
        self.assertIsInstance(loaded_node_options, dict)
        node_options = {
            "name": "test-1",
            "disk_image_path": test_image,
            "memory_size": "1024MiB",
            **loaded_node_options,
        }

        node = await create(self.client, **node_options)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, Node)
        self.assertTrue(await remove(self.client, node.id))

    async def test_stop_node(self):
        test_image = self.datastore.realpath(
            join(self.images_dir, f"{self.name}-Rocky-9-1.qcow2")
        )
        # Load architecture node_options
        node_options_path = join("res", "node_options", f"{self.architecture}.json")
        loaded_node_options = load_json(node_options_path)
        self.assertIsInstance(loaded_node_options, dict)
        node_options = {
            "name": "test-2",
            "disk_image_path": test_image,
            "memory_size": "1024MiB",
            **loaded_node_options,
        }

        new_node = await create(self.client, **node_options)
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
