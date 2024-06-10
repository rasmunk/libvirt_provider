async def ls(client, **kwargs):
    response = {}
    instances = client.ls(**kwargs)
    if instances is None or not isinstance(instances, (list, tuple, set)):
        response["msg"] = "Failed to list instances"
        return False, response

    response["instances"] = instances
    response["msg"] = "Instances"
    return True, response
