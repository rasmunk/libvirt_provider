import libvirt
import uuid
import jinja2
from libvirt_provider.utils.io import load, load_json


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

    def create(self, name, template_path=None, **kwargs):
        if not template_path:
            created_id = self._create(name=name, **kwargs)
        else:
            created_id = self._create_from_template(name, template_path, **kwargs)
        if not created_id:
            return False
        return self.get(created_id)

    def _load_jinja_template(self, path):
        template_content = load(path)
        if not template_content:
            return None
        return jinja2.Template(template_content)

    def _create_from_template(self, name, path, **kwargs):
        if ".j2" in path:
            template_content = self._load_jinja_template(path)
            if not template_content:
                return None
            xml_desc = template_content.render(name=name, **kwargs)
        elif ".json" in path:
            template_content = load_json(path)
            if not template_content:
                return None
            template_content["name"] = name
            template_content = template_content.update(kwargs)
            xml_desc = template_content
        else:
            # Expect it just to be a string template
            template_content = load(path)
            if not template_content:
                return None
            xml_desc = template_content.format(name=name, **kwargs)

        if not xml_desc:
            return None
        domain = self._conn.createXML(xml_desc)
        if domain:
            return domain.UUIDString()
        return None

    def _create(
        self,
        domain_type="kvm",
        name=None,
        disk_type="file",
        disk_driver_type="qcow2",
        disk_image_path=None,
        disk_target_dev="hda",
        disk_target_bus="ide",
        memory_size="1024",
        num_vcpus=1,
        cpu_architecture="x86_64",
        machine="pc",
        serial_type="pty",
        serial_type_target_port=0,
        console_type="pty",
    ):
        xml_desc = f"""
        <domain type='{domain_type}'>
          <name>{name}</name>
          <memory>{memory_size}</memory>
          <vcpu>{num_vcpus}</vcpu>
          <os>
            <type arch='{cpu_architecture}' machine='{machine}'>hvm</type>
          </os>
          <devices>
            <emulator>/usr/bin/qemu-system-{cpu_architecture}</emulator>
            <disk type='{disk_type}' device='disk'>
              <driver name='qemu' type='{disk_driver_type}'/>
              <source file='{disk_image_path}'/>
              <target dev='{disk_target_dev}' bus='{disk_target_bus}'/>
            </disk>
            <serial type='{serial_type}'>
              <target port='{serial_type_target_port}'/>
            </serial>
            <console type='{console_type}'>
              <target type='serial' port='{serial_type_target_port}'/>
            </console>
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
