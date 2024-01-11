import libvirt
import uuid


class Node:
    def __init__(self, id, name, **kwargs):
        self.id = id
        self.name = name
        self.state = None
        self.config = kwargs

    def print_state(self):
        print("Node: {} - {} - {}".format(self.id, self.name, self.config))


class DummyDriver:
    def __init__(self, *args, **kwargs):
        pass

    def create(self, name, **kwargs):
        return Node(str(uuid.uuid4()), name, **kwargs)

    def get(self, node_id):
        return Node(str(uuid.uuid4()), "dummy-node")

    def start(self, node):
        return True

    def stop(self, node):
        return True

    def remove(self, node):
        return True


def auth_callback(creds, callback_data):
    print("Hello from auth")
    return 0


class LibvirtDriver:
    def __init__(self, *args, open_uri=None, **kwargs):
        if not open_uri:
            self._open_uri = "qemu:///session"
        else:
            self._open_uri = open_uri
        # From virt-manager/virtinst/connection.py
        # Mirror the set of libvirt.c virConnectCredTypeDefault
        valid_auth_options = [
            libvirt.VIR_CRED_AUTHNAME,
            libvirt.VIR_CRED_ECHOPROMPT,
            libvirt.VIR_CRED_REALM,
            libvirt.VIR_CRED_PASSPHRASE,
            libvirt.VIR_CRED_NOECHOPROMPT,
            libvirt.VIR_CRED_EXTERNAL,
        ]
        flags = 0
        auth_list = [valid_auth_options, auth_callback, None]
        self._conn = libvirt.openAuth(self._open_uri, auth_list, flags)

    def close(self):
        self._conn.close()

    def get(self, node_id):
        domain = self._get(node_id)
        if not domain:
            return False
        state = domain.state()
        return Node(
            domain.UUIDString(), domain.name(), state=state, config=domain.XMLDesc()
        )

    def _get(self, node_id):
        try:
            domain = self._conn.lookupByUUIDString(node_id)
            return domain
        except libvirt.libvirtError as err:
            print("Failed to lookup domain: {} - {}".format(node_id, err))
            return False
        return False

    def create(self, name, **kwargs):
        created_id = self._create(name=name, **kwargs)
        if not created_id:
            return False
        return self.get(created_id)

    def _create(
        self,
        name=None,
        disk_image_path=None,
        memory_size="1024",
        num_vcpus=1,
        cpu_architecture="x86_64",
        machine="pc",
    ):
        xml_desc = f"""
        <domain type='kvm'>
          <name>{name}</name>
          <metadata>
          </metadata>
          <memory>{memory_size}</memory>
          <vcpu>{num_vcpus}</vcpu>
          <os>
            <type arch='{cpu_architecture}' machine='{machine}'>hvm</type>
          </os>
          <devices>
            <disk type='file' device='disk'>
              <driver name='qemu' type='qcow2'/>
              <source file='{disk_image_path}'/>
              <target dev='hda' bus='ide'/>
            </disk>
          </devices>
        </domain>
        """
        domain = self._conn.createXML(xml_desc)
        if not domain:
            return None
        return domain.UUIDString()

    def start(self, node_id):
        domain = self._get(node_id)
        if not domain:
            return False
        try:
            domain.resume()
        except libvirt.libvirtError as err:
            print("Failed to resume domain: {} - {}".format(node_id, err))
            return False
        return True

    def state(self, node_id):
        domain = self._get(node_id)
        if not domain:
            return False
        try:
            return domain.state()
        except libvirt.libvirtError as err:
            print("Failed to get domain state: {} - {}".format(node_id, err))
            return False
        return False

    def stop(self, node_id):
        domain = self._get(node_id)
        if not domain:
            return False
        try:
            domain.shutdown()
        except libvirt.libvirtError as err:
            print("Failed to shutdown domain: {} - {}".format(node_id, err))
            return False
        return True

    def remove(self, node_id):
        domain = self._get(node_id)
        if not domain:
            return False
        try:
            domain.destroy()
        except libvirt.libvirtError as err:
            print("Failed to destroy domain: {} - {}".format(node_id, err))
            return False
        return True
