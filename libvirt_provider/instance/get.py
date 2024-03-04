async def get(client, id):
    response = {}
    instance = client.get(id)
    if not instance:
        response["msg"] = f"Failed to get instance: {id}"
        return False, response

    response["instance"] = instance
    response["msg"] = "Found instance"
    return True, response
