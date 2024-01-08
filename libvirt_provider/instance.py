async def list_instances(client):
    return client.list_nodes()


async def create(client, instance_options):
    instance_args = []
    instance_kwargs = {}

    # Load domain
    domain = client.lookupByName(instance_options["domain"])
    if not domain:
        return False
    return domain.create()


async def start(client):
    instance = get_instance(client, instance_id)
    if not instance:
        return False
    return client.ex_start_node(instance)


async def destroy(client, instance_id):
    instance = get_instance(client, instance_id)
    if not instance:
        return False
    return client.destroy_node(instance)
