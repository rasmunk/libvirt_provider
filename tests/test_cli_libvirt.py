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

import os
import json
import unittest
import random
from io import StringIO
from unittest.mock import patch
from libvirt_provider.defaults import INSTANCE
from libvirt_provider.codes import SUCCESS
from libvirt_provider.cli.cli import main
from libvirt_provider.utils.io import copy, exists
from tests.context import LibvirtTestContext


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
