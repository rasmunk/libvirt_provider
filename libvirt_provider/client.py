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

from libvirt_provider.defaults import LIBVIRT, CONTAINER, DUMMY
from libvirt_provider.models import DummyDriver, LibvirtDriver, LXCDriver


def discover_provider_client(provider):
    if provider == LIBVIRT:
        return LibvirtDriver
    if provider == CONTAINER:
        return LXCDriver
    elif provider == DUMMY:
        return DummyDriver
    else:
        raise RuntimeError("Unknown provider: {}".format(provider))


def new_client(provider, *args, **kwargs):
    # Discover driver
    driver = discover_provider_client(provider)
    return driver(*args, **kwargs)
