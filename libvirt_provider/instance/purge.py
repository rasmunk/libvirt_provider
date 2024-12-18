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


async def purge(client, force=False, regex=None):
    response = {}
    instances = client.ls(regex=regex)
    if not instances and isinstance(instances, bool):
        response["msg"] = "Failed to list instances"
        return False, response

    purged, failed = client.purge(instances, force=force)
    response["msg"] = "Instances purge results"
    response["purged"] = purged
    response["failed"] = failed
    if failed:
        return False, response
    return True, response
