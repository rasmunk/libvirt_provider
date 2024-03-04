async def state(client, id):
    response = {}
    state = client.state(id)
    if not state:
        response["msg"] = f"Failed to get state for instance: {id}"
        return False, response

    response["state"] = state
    response["msg"] = f"Found for instance: {id}"
    return True, response
