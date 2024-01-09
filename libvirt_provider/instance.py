async def get_instance(client, instance_id):
    return client.get(instance_id)


async def create(client, instance_options):
    return client.create(**instance_options)


async def start(client, instance_id):
    return client.start(instance_id)


async def remove(client, instance_id):
    return client.remove(instance_id)
