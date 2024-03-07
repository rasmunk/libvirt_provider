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
        print(
            "Node id: {}, name: {}, state: {}, config: {}".format(
                self.id, self.name, self.state, self.config
            )
        )

    def __str__(self):
        return "Node id: {}, name: {}, state: {}, config: {}".format(
            self.id, self.name, self.state, self.config
        )

    def asdict(self):
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "config": self.config,
        }


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

    def ls(self):
        return [Node(str(uuid.uuid4()), "dummy-node-{}".format(i)) for i in range(4)]


def auth_callback(creds, callback_data):
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

    def create(self, name, disk_image_path, template_path=None, **kwargs):
        if "memory_size" in kwargs:
            kwargs["memory_size"] = self._prepare_memory(kwargs["memory_size"])

        if not template_path:
            created_id = self._create(
                name=name, disk_image_path=disk_image_path, **kwargs
            )
        else:
            created_id = self._create_from_template(
                name, template_path, disk_image_path=disk_image_path, **kwargs
            )
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
        domain = self._create_xml(xml_desc)
        if domain:
            return domain.UUIDString()
        return None

    def _create(
        self,
        domain_type="qemu",
        name=None,
        disk_device_type="file",
        disk_driver_name="qemu",
        disk_driver_type="qcow2",
        disk_image_path=None,
        disk_target_dev="hda",
        disk_target_bus="ide",
        memory_size="1024MiB",
        num_vcpus=1,
        cpu_architecture="x86_64",
        cpu_mode="host-model",
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
          <cpu mode='{cpu_mode}'/>
          <devices>
            <disk type='{disk_device_type}' device='disk'>
              <driver name='{disk_driver_name}' type='{disk_driver_type}'/>
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
        domain = self._create_xml(xml_desc)
        if not domain:
            return None
        return domain.UUIDString()

    def _prepare_memory(self, memory_size):
        # memory_size is interpreted as KiB when passed to libvirt, allow for conversion from multiple units
        expanded_memory_size = None
        if "kib" in memory_size.lower() or "ki" in memory_size.lower():
            expanded_memory_size = int(
                memory_size.lower().replace("kib", "").replace("ki", "")
            )
        elif "mib" in memory_size.lower() or "mi" in memory_size.lower():
            expanded_memory_size = (
                int(memory_size.lower().replace("mib", "").replace("mi", "")) * 1024
            )
        elif "mb" in memory_size.lower() or "m" in memory_size.lower():
            expanded_memory_size = (
                int(memory_size.lower().replace("mb", "").replace("m", "")) * 1000
            )
        elif "gib" in memory_size.lower() or "gi" in memory_size.lower():
            expanded_memory_size = (
                int(memory_size.lower().replace("gib", "").replace("gi", ""))
                * 1024
                * 1024
            )
        elif "gb" in memory_size.lower() or "g" in memory_size.lower():
            expanded_memory_size = (
                int(memory_size.lower().replace("gb", "").replace("g", ""))
                * 1000
                * 1000
            )
        elif "tib" in memory_size.lower() or "ti" in memory_size.lower():
            expanded_memory_size = (
                int(memory_size.lower().replace("tib", "").replace("ti", ""))
                * 1024
                * 1024
                * 1024
            )
        elif "tb" in memory_size.lower() or "t" in memory_size.lower():
            expanded_memory_size = (
                int(memory_size.lower().replace("tb", "").replace("t", ""))
                * 1000
                * 1000
                * 1000
            )
        else:
            expanded_memory_size = int(memory_size)
        return expanded_memory_size

    def _create_xml(self, xml):
        return self._conn.createXML(xml)

    def show(self, node_id):
        return self.get(node_id)

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

    def ls(self):
        domains = self._conn.listAllDomains()
        if domains is None or not isinstance(domains, (tuple, set, list)):
            return False
        return [self.get(domain.UUIDString()) for domain in domains]


class LXCDriver(LibvirtDriver):
    def __init__(self, *args, open_uri=None, **kwargs):
        if not open_uri:
            self._open_uri = "lxc:///system"
        else:
            self._open_uri = open_uri
        super().__init__(*args, open_uri=open_uri, **kwargs)

    def _create(
        self,
        domain_type="lxc",
        name=None,
        memory_size="1024",
        num_vcpus=1,
        on_poweroff="destroy",
        on_reboot="restart",
        on_crash="destroy",
        emulator="/usr/libexec/libvirt_lxc",
        console_type="pty",
    ):
        xml_desc = f"""
        <domain type='{domain_type}'>
            <name>{name}</name>
            <memory>{memory_size}</memory>
            <os>
                <type>exe</type>
                <init>/bin/sh</init>
            </os>
            <vcpu>{num_vcpus}</vcpu>
            <clock offset='utc'/>
            <on_poweroff>{on_poweroff}</on_poweroff>
            <on_reboot>{on_reboot}</on_reboot>
            <on_crash>{on_crash}</on_crash>
            <devices>
                <emulator>{emulator}</emulator>
                <interface type='network'>
                    <source network='default'/>
                </interface>
                <console type='{console_type}' />
            </devices>
        </domain>
        """
        domain = self._create_xml(xml_desc)
        if not domain:
            return None
        return domain.UUIDString()

    def create(self, name, template_path=None, **kwargs):
        if not template_path:
            created_id = self._create(name=name, **kwargs)
        else:
            created_id = self._create_from_template(name, template_path, **kwargs)
        if not created_id:
            return False
        return self.get(created_id)

    def get(self, container_id):
        raise NotImplementedError

    def start(self, container):
        raise NotImplementedError

    def stop(self, container):
        raise NotImplementedError

    def remove(self, container):
        raise NotImplementedError

    def ls(self):
        raise NotImplementedError
