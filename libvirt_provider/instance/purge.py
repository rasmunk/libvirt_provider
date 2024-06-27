async def purge(client, force=False, regex=None):
    response = {}
    instances = client.ls(regex=regex)
    if not instances and isinstance(instances, bool):
        response["msg"] = "Failed to list instances"
        return False, response

    purged, failed = client.purge(instances, force=force)
    response["msg"] = "Instances purge results"
    response["purged"] = purged
    response["failed"] = failed
    if failed:
        return False, response
    return True, response
