async def start(client, id):
    response = {}
    started = client.start(id)
    if not started:
        response["msg"] = f"Failed to start instance: {id}"
        return False, response
    response["msg"] = f"Started instance: {id}"
    return True, response
