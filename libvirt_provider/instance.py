async def get_instance(client, instance_id):
    return client.get(instance_id)


async def list_instances(client):
    return client.list_nodes()


async def create(client, instance_options):
    return client.create(**instance_options)


async def start(client):
    instance = await get_instance(client, instance_id)
    if not instance:
        return False
    return client.ex_start_node(instance)


async def destroy(client, instance_id):
    instance = client.get(instance_id)

    if not instance:
        return False
    return client.destroy_node(instance)
