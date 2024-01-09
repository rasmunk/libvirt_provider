import shelve


def load(path, name):
    with shelve.open(path) as db:
        return db.get("nodes")


def write(path, content):
    with shelve.open(path) as db:
        db["nodes"] = content
