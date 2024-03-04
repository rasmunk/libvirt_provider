async def list(client):
    response = {}
    instances = client.list()
    if not instances:
        response["msg"] = "Failed to list instances"
        return False, response

    response["instances"] = instances
    response["msg"] = "Instances"
    return True, response
