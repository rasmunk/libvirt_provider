import shelve
from libvirt_provider.models import Node
from libvirt_provider.utils.io import acquire_lock, release_lock


class Pool:
    def __init__(self, name):
        # The name of the pool is equal to the
        # database name
        self.name = name
        self._lock_path = "{}.lock".format(self.name)

    async def items(self):
        with shelve.open(self.name) as db:
            return [item for item in db.values()]

    async def add(self, item):
        locked = acquire_lock(self._lock_path)
        if not locked:
            return False

        with shelve.open(self.name) as db:
            db[item.id] = item

        release_lock(locked)
        return True

    async def remove(self, item_id):
        locked = acquire_lock(self._lock_path)
        if not locked:
            return False

        with shelve.open(self.name) as db:
            db.pop(item_id)

        release_lock(locked)
        return True

    async def get(self, item_id):
        with shelve.open(self.name) as db:
            return db.get(item_id)
