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

import platform
import os
import json
import unittest
import random
import xml.etree.ElementTree as ET
from io import StringIO
from unittest.mock import patch
from libvirt_provider.defaults import INSTANCE
from libvirt_provider.codes import SUCCESS
from libvirt_provider.cli.cli import main
from libvirt_provider.utils.io import copy, exists, join
from tests.context import LibvirtTestContext, TEST_JINJA_TEMPLATE


def cli_action(action, *action_args):
    return_code = None
    try:
        args = [INSTANCE, action]
        args.extend(*action_args)
        return_code = main(args)
    except SystemExit as e:
        return_code = e.code
    return return_code


def create_instance(instance_name, instance_disk_path, instance_args):
    args = [instance_name, instance_disk_path, *instance_args]
    return cli_action("create", args)


def ls_instance(regex):
    args = ["--regex", regex]
    return cli_action("ls", args)


def remove_instance(instance_id):
    args = [instance_id]
    return cli_action("remove", args)


def purge_instances(regex):
    args = ["--regex", regex]
    return cli_action("purge", args)


def show_instance(instance_id):
    args = [instance_id]
    return cli_action("show", args)


def json_to_dict(json_str):
    return json.loads(json_str)


class TestCLILibvirt(unittest.IsolatedAsyncioTestCase):
    context = LibvirtTestContext()

    async def asyncSetUp(self):
        await self.context.setUp()

        self.seed = str(random.random())[2:10]
        self.name = f"libvirt-cli-libvirt-{self.context.architecture}-{self.seed}"

        context_image_split = self.context.image.split(".")
        new_test_image = "{}-{}.{}".format(
            context_image_split[0], self.name, context_image_split[-1]
        )

        self.test_image = os.path.realpath(new_test_image)
        self.assertTrue(copy(self.context.image, self.test_image))
        self.assertTrue(exists(self.test_image))

        nested_common_args = [
            "--{} {}".format(option.replace("_", "-"), value)
            for option, value in self.context.common_node_options.items()
        ]

        self.common_instance_args = [
            arg for args_pair in nested_common_args for arg in args_pair.split(" ")
        ]

    async def asyncTearDown(self):
        pass
        # TODO add the general purge of test instances
        # Purge all test related instances
        # search_regex = "{}.*".format(self.name)
        # purge_return_code = purge_instances(search_regex)
        # self.assertEqual(purge_return_code, SUCCESS)

    @classmethod
    def tearDownClass(cls):
        cls.context.tearDown()

    def test_cli_create_instance(self):
        test_name = "{}-test-cli-create-instance".format(self.name)
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            return_code = create_instance(
                test_name, self.test_image, self.common_instance_args
            )
            self.assertEqual(return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("instance", output)

            instance = output["instance"]
            self.assertIsInstance(instance, dict)
            self.assertIn("name", instance)
            self.assertEqual(instance["name"], test_name)
            self.assertIn("id", instance)

    def test_cli_create_instance_jinja_template_override(self):
        test_name = "{}-test-cli-create-instance-jinja".format(self.name)
        template_path = join(self.context.test_templates_directory, TEST_JINJA_TEMPLATE)
        template_args = [
            *self.common_instance_args,
            "--memory-size",
            "2048MiB",
            "--template-path",
            template_path,
            "--extra-template-path-values",
            "memory_size=1024MiB",
        ]
        expected_memory_kib_size = 1024 * 1024
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            return_code = create_instance(test_name, self.test_image, template_args)
            self.assertEqual(return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("instance", output)
            self.assertIn("config", output["instance"])
            self.assertIn("config", output["instance"]["config"])
            config = output["instance"]["config"]["config"]
            self.assertIsInstance(config, str)
            tree = ET.ElementTree(ET.fromstring(config))
            memory_tree_node = [child for child in tree.iter() if child.tag == "memory"]
            self.assertEqual(len(memory_tree_node), 1)
            instance_memory_kib = int(memory_tree_node[0].text)
            self.assertEqual(instance_memory_kib, expected_memory_kib_size)

    def test_cli_create_instance_advanced_jinja_template(self):
        test_name = "{}-test-cli-create-instance-advanced-jinja".format(self.name)
        template_path = join(self.context.test_templates_directory, TEST_JINJA_TEMPLATE)
        expected_num_vcpus = 1
        expected_memory_size = "1024MiB"
        expected_cpu_architecture = platform.machine()
        template_args = [
            *self.common_instance_args,
            "--template-path",
            template_path,
            "--extra-template-path-values",
            "num_vcpus={},memory_size={},cpu_architecture={}".format(
                expected_num_vcpus,
                expected_memory_size,
                expected_cpu_architecture,
            ),
        ]
        expected_memory_kib_size = 1024 * 1024
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            return_code = create_instance(test_name, self.test_image, template_args)
            self.assertEqual(return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(output, dict)
            self.assertIn("instance", output)
            self.assertIn("config", output["instance"])
            self.assertIn("config", output["instance"]["config"])
            config = output["instance"]["config"]["config"]
            self.assertIsInstance(config, str)

            tree = ET.ElementTree(ET.fromstring(config))
            vcpu_tree_node = tree.find("vcpu")
            self.assertIsNotNone(vcpu_tree_node)
            instance_num_vcpus = int(vcpu_tree_node.text)
            self.assertEqual(instance_num_vcpus, expected_num_vcpus)

            memory_tree_node = tree.find("memory")
            self.assertIsNotNone(memory_tree_node)
            instance_memory_kib = int(memory_tree_node[0].text)
            self.assertEqual(instance_memory_kib, expected_memory_kib_size)

            os_tree_node = tree.find("os").find("type")
            self.assertIsNotNone(os_tree_node)
            cpu_architecture = os_tree_node.attrib["arch"]
            self.assertEqual(cpu_architecture, expected_cpu_architecture)

    def test_cli_ls_instances(self):
        test_name = "{}-test-cli-ls-instance".format(self.name)
        create_return_code = create_instance(
            test_name, self.test_image, self.common_instance_args
        )
        self.assertEqual(create_return_code, SUCCESS)

        instance_id = None
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            search_regex = "{}.*".format(test_name)
            ls_return_code = ls_instance(search_regex)
            self.assertEqual(ls_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            # Verify the ls output structure and the identification content
            self.assertIsInstance(output, dict)
            self.assertIn("instances", output)

            instances = output["instances"]
            self.assertIsInstance(instances, list)
            self.assertEqual(len(instances), 1)

            instance = instances[0]
            self.assertIn("name", instance)
            self.assertEqual(instance["name"], test_name)

            instance_id = instance["id"]
            self.assertIsNotNone(instance_id)

    def test_cli_show_instance(self):
        test_name = "{}-test-cli-show-instance".format(self.name)
        instance_id = None
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            create_return_code = create_instance(
                test_name, self.test_image, self.common_instance_args
            )
            self.assertEqual(create_return_code, SUCCESS)
            create_output = json_to_dict(captured_stdout.getvalue())
            instance_id = create_output["instance"]["id"]

        self.assertIsNotNone(instance_id)
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            show_return_code = show_instance(instance_id)
            self.assertEqual(show_return_code, SUCCESS)
            show_output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(show_output, dict)
            self.assertIn("instance", show_output)

            instance = show_output["instance"]
            self.assertIsInstance(instance, dict)
            self.assertIn("name", instance)
            self.assertEqual(instance["name"], test_name)
            self.assertIn("id", instance)
            self.assertEqual(instance["id"], instance_id)

    def test_cli_remove_instance(self):
        test_name = "{}-test-cli-remove-instance".format(self.name)
        instance_id = None
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            create_return_code = create_instance(
                test_name, self.test_image, self.common_instance_args
            )
            self.assertEqual(create_return_code, SUCCESS)
            create_output = json_to_dict(captured_stdout.getvalue())
            instance_id = create_output["instance"]["id"]

        self.assertIsNotNone(instance_id)
        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            remove_return_code = remove_instance(instance_id)
            self.assertEqual(remove_return_code, SUCCESS)
            remove_output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(remove_output, dict)

            self.assertIn("id", remove_output)
            self.assertEqual(remove_output["id"], instance_id)

            self.assertIn("status", remove_output)
            self.assertEqual(remove_output["status"], "success")

    def test_cli_purge_instances(self):
        num_test_instances = 5
        base_test_name = "{}-test-cli-purge-instance".format(self.seed)
        test_names = [
            "{}-{}".format(base_test_name, num_test)
            for num_test in range(num_test_instances)
        ]

        instance_ids = []
        for test_name in test_names:
            with patch("sys.stdout", new=StringIO()) as captured_stdout:
                create_return_code = create_instance(
                    test_name, self.test_image, self.common_instance_args
                )
                self.assertEqual(create_return_code, SUCCESS)
                create_output = json_to_dict(captured_stdout.getvalue())
                instance_ids.append(create_output["instance"]["id"])
        self.assertEqual(len(instance_ids), num_test_instances)

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            search_regex = "{}.*".format(base_test_name)
            purged_return_code = purge_instances(search_regex)
            self.assertEqual(purged_return_code, SUCCESS)

            purge_output = json_to_dict(captured_stdout.getvalue())
            self.assertIsInstance(purge_output, dict)
            self.assertIn("purged", purge_output)

            purged_instances = purge_output["purged"]
            self.assertCountEqual(instance_ids, purged_instances)

            self.assertIn("failed", purge_output)
            self.assertEqual(purge_output["failed"], [])

        with patch("sys.stdout", new=StringIO()) as captured_stdout:
            search_regex = "{}.*".format(base_test_name)
            ls_return_code = ls_instance(search_regex)
            self.assertEqual(ls_return_code, SUCCESS)
            output = json_to_dict(captured_stdout.getvalue())
            # Verify the ls output structure and the identification content
            self.assertIsInstance(output, dict)
            self.assertNotIn("purged", output)
            self.assertIn("instances", output)
            self.assertEqual(output["instances"], [])
