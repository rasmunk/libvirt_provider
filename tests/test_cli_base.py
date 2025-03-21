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
from libvirt_provider.codes import SUCCESS
from libvirt_provider.cli.cli import main


class TestCLIBase(unittest.TestCase):

    def test_cli_help(self):
        return_code = None
        try:
            return_code = main(["--help"])
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

    def test_cli_version(self):
        return_code = None
        try:
            return_code = main(["--version"])
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)
