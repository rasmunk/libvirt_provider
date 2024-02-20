async def get(client, instance_id):
    return client.get(instance_id)


async def create(client, *instance_args, **instance_options):
    return client.create(*instance_args, **instance_options)


async def start(client, instance_id):
    return client.start(instance_id)


async def state(client, instance_id):
    return client.state(instance_id)


async def stop(client, instance_id):
    return client.stop(instance_id)


async def remove(client, instance_id):
    return client.remove(instance_id)
