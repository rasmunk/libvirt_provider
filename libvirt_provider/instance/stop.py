async def stop(client, id):
    response = {}
    stopped = client.stop(id)
    if not stopped:
        response["msg"] = f"Failed to stop instance: {id}"
        return False, response

    response["msg"] = f"Stopped instance: {id}"
    return True, response
