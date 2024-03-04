async def remove(client, id):
    response = {}
    removed = client.remove(id)
    if not removed:
        response["msg"] = f"Failed to remove container: {id}"
        return False, response
    response["msg"] = f"Removed container: {id}"
    return True, response
