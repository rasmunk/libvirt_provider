async def ls(client):
    response = {}
    containers = client.ls()
    if not containers:
        response["msg"] = "Failed to list containers"
        return False, response

    response["containers"] = containers
    response["msg"] = "containers"
    return True, response
