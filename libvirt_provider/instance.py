from libcloud.compute.base import Node, NodeAuthSSHKey, NodeAuthPassword
from libvirt_provider.helpers import new_apache_client


def valid_instance(instance):
    if not isinstance(instance, Node):
        raise TypeError("The Instance must be of type libcloud.compute.base.Node")
    return True


def get_instance_by_name(client, name):
    try:
        instances = client.list_nodes()
    except Exception as err:
        print(err)
        return None

    if instances:
        for instance in instances:
            if instance.name == name:
                return instance
    return None


def get_instance(client, instance_id, *args, **kwargs):
    try:
        instances = client.list_nodes(*args, **kwargs)
    except Exception as err:
        print(err)
        return None

    if instances:
        for instance in instances:
            if instance.id == instance_id:
                return instance
    return None


def client_get_instance(provider, provider_kwargs, format_return=False, instance=None):
    client = new_apache_client(provider, provider_kwargs)
    found_instance = get_instance(client, instance["uuid"])
    if found_instance:
        if format_return:
            return found_instance.uuid, str(found_instance), ""
        return found_instance.uuid, found_instance, ""
    return None, None, "Failed to find an instance with: {} details".format(instance)


def client_delete_instance(provider, provider_kwargs, instance=None, **kwargs):
    client = new_apache_client(provider, provider_kwargs, **kwargs)
    found_instance = get_instance(client, instance["uuid"])
    if found_instance:
        deleted = delete_instance(client, found_instance)
        if deleted:
            return found_instance.uuid, ""
        return False, "Failed to delete: {}".format(found_instance.uuid)
    return False, "Could not find: {}".format(**instance)


def delete_instance(client, instance):
    return client.destroy_node(instance)


def client_list_instances(provider, provider_kwargs, format_return=False, **kwargs):
    client = new_apache_client(provider, provider_kwargs, **kwargs)
    instances = list_instances(client)
    if format_return:
        return [str(i) for i in instances]
    return instances


def list_instances(client):
    return client.list_nodes()


def create(client, instance_options):
    instance_args = []
    instance_kwargs = {}

    if "name" not in instance_options:
        raise RuntimeError(
            "Failed to find the required 'name' key in: {}".format(instance_options)
        )
    instance_args.append(instance_options["name"])

    selected_size = None
    available_sizes = client.list_sizes()
    for size in available_sizes:
        if size.name == instance_options["size"]:
            selected_size = size

    if not selected_size:
        raise RuntimeError(
            "Failed to find an appropriate size: {} in: {}".format(
                selected_size, available_sizes
            )
        )
    instance_args.append(selected_size)

    image = None
    # Only get the image if the underlying driver has it implemented
    try:
        image = client.get_image(instance_options["image"])
        if not image:
            raise RuntimeError(
                "Failed to find the appropriate image: {}".format(
                    instance_options["image"]
                )
            )
    except NotImplementedError:
        print("The underlying driver does not support get_image, default to None")
    # The API requires that the image positional argument is given, even if it is
    # not used
    instance_args.append(image)

    auth = None
    # Since only one auth is supported, take the first credentials
    if "credential" in instance_options:
        credential = instance_options["credential"]
        if credential.password:
            auth = NodeAuthPassword(credential.password)
        if credential.public_key:
            # libcloud expected the NodeAuthSSHKey string to be a
            # 3 component string seperated by spaces
            # {type} {key} {comment}
            auth = NodeAuthSSHKey(credential.public_key)
        instance_kwargs["auth"] = auth

    return client.create_node(*instance_args, **instance_kwargs)


def destroy(client, instance_id):
    instance = get_instance(client, instance_id)
    if not instance:
        return False
    return client.destroy_node(instance)
