async def show(client, id):
    response = {}
    instance = client.show(id)
    if not instance:
        response["msg"] = f"Failed to show instance: {id}"
        return False, response

    response["instance"] = instance
    response["msg"] = "Found instance"
    return True, response
