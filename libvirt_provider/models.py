import libvirt
import uuid


class Node:
    def __init__(self, id, name, image, size):
        self.id = id
        self.name = name
        self.image = image
        self.size = size

    def print_state(self):
        print(
            "Node: {} - {} - {} - {}".format(self.id, self.name, self.image, self.size)
        )


class DummyDriver:
    def __init__(self, *args, **kwargs):
        pass

    def create(self, name=None, image=None, size=None):
        return Node(str(uuid.uuid4()), name, image, size)

    def get(self, node_id):
        return Node(str(uuid.uuid4()), "dummy-1", "dummy-image", "Small")

    def start(self, node):
        return True

    def stop(self, node):
        return True

    def remove(self, node):
        return True


class LibvirtDriver:
    def __init__(self, *args, **kwargs):
        pass

    def create(self, name=None, image=None, size=None):
        return Node(name, image, size)

    def start(self, node_id):
        return True

    def stop(self, node_id):
        return True

    def remove(self, node_id):
        return True
