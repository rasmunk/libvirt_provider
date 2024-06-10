import shelve
from libvirt_provider.utils.io import acquire_lock, release_lock, exists
from libvirt_provider.utils.io import remove as fs_remove


class Pool:
    def __init__(self, name):
        # The name of the pool is equal to the
        # database name
        self.name = name
        self._database_path = "{}.db".format(self.name)
        self._lock_path = "{}.lock".format(self.name)

    async def items(self):
        with shelve.open(self.name) as db:
            return [item for item in db.values()]

    async def add(self, item):
        if not hasattr(item, "id"):
            raise AttributeError(
                "add item must have an 'id' attribute to be added to the pool"
            )

        lock = acquire_lock(self._lock_path)
        if not lock:
            return False
        try:
            with shelve.open(self.name) as db:
                db[item.id] = item
        except Exception as err:
            print(err)
            return False
        finally:
            release_lock(lock)
        return True

    async def remove(self, item_id):
        lock = acquire_lock(self._lock_path)
        if not lock:
            return False
        try:
            with shelve.open(self.name) as db:
                db.pop(item_id)
        except Exception as err:
            print(err)
            return False
        finally:
            release_lock(lock)
        return True

    async def remove_persistence(self):
        lock = acquire_lock(self._lock_path)
        if not lock:
            return False
        try:
            if exists(self._database_path):
                if not fs_remove(self._database_path):
                    return False
            if exists(self._lock_path):
                if not fs_remove(self._lock_path):
                    return False
        except Exception as err:
            print(err)
            return False
        finally:
            release_lock(lock)
        return True

    async def get(self, item_id):
        with shelve.open(self.name) as db:
            return db.get(item_id)

    async def flush(self):
        lock = acquire_lock(self._lock_path)
        if not lock:
            return False

        try:
            with shelve.open(self.name) as db:
                [db.pop(item_id) for item_id in db.keys()]
        except Exception as err:
            print(err)
            return False
        finally:
            release_lock(lock)
        return True
