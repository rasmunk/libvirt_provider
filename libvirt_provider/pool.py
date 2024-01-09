import shelve
from libvirt_provider.models import Node
from libvirt_provider.utils.io import acquire_lock, release_lock, write, load


class Pool:
    def __init__(self, name):
        self.name = name
        self._nodes = []

    async def nodes(self):
        return self._nodes

    async def add_node(self, node):
        aquired_lock = aquired_lock(self.name)
        if not aquired_lock:
            return False

        with shelver.open(self.name) as db:
            db[node.id] = node

        release_lock(aquired_lock)
        return True

    async def remove_node(self, node_id):
        aquired_lock = acquire_lock(self.name)
        with shelve.open(self.name) as db:
            del db[node_id]
        release_lock(aquired_lock)
        return True
