async def create(client, *args, **kwargs):
    response = {}
    instance = client.create(*args, **kwargs)
    if not instance:
        response["msg"] = "Failed to create instance"
        return False, response

    response["instance"] = instance
    response["msg"] = "Created instance"
    return True, response
