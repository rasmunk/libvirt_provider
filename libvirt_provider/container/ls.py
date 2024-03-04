async def ls(client):
    response = {}
    containers = client.list()
    if not containers:
        response["msg"] = "Failed to list containers"
        return False, response

    response["containers"] = containers
    response["msg"] = "containers"
    return True, response
