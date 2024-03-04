async def create(client, *args, **kwargs):
    response = {}
    container = client.create(*args, **kwargs)
    if not container:
        response["msg"] = "Failed to create container"
        return False, response

    response["container"] = container
    response["msg"] = "Created container"
    return True, response
