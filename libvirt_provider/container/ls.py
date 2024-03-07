async def ls(client):
    response = {}
    containers = client.ls()
    if containers is None or not isinstance(containers, (list, tuple, set)):
        response["msg"] = "Failed to list containers"
        return False, response

    response["containers"] = containers
    response["msg"] = "containers"
    return True, response
