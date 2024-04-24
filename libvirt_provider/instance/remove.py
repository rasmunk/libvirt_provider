async def remove(client, id):
    response = {}
    removed = client.remove(id)
    if not removed:
        response["msg"] = f"Failed to remove instance: {id}"
        return False, response
    response["id"] = id
    response["msg"] = "Removed instance"
    return True, response
