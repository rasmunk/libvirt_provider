async def get(client, id):
    response = {}
    container = client.get(id)
    if not container:
        response["msg"] = f"Failed to get container: {id}"
        return False, response

    response["container"] = container
    response["msg"] = "Found container"
    return True, response
