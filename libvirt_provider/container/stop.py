async def stop(client, id):
    response = {}
    stopped = client.stop(id)
    if not stopped:
        response["msg"] = f"Failed to stop container: {id}"
        return False, response

    response["msg"] = f"Stopped container: {id}"
    return True, response
