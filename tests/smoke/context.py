from gen_vm_image.cli.build_image import build_architecture
from libvirt_provider.utils.io import remove as fs_remove
from libvirt_provider.utils.user import (
    find_user_with_username,
    find_group_with_groupname,
)
from libvirt_provider.utils.io import (
    join,
    exists,
    makedirs,
)


class LibvirtTestContext:
    def __init__(self):
        self.init_done = False

    async def setUp(self):
        if self.init_done:
            return

        user_base = "qemu"
        self.user = find_user_with_username(user_base)
        assert self.user is not False
        self.group = find_group_with_groupname(user_base)
        assert self.group is not False

        self.architecture = "x86_64"
        self.image_version = "12"
        self.name = f"libvirt-{self.architecture}"
        # Note, a properly SELinux labelled directory is required when SELinux is enabled
        self.images_dir = join("tests", "images", self.architecture)
        if not exists(self.images_dir):
            assert makedirs(self.images_dir)

        architecture_path = join(
            "tests", "smoke", "res", "gen-vm-image", "architecture.yml"
        )
        assert exists(architecture_path)
        self.image = join(self.images_dir, f"{self.name}-{self.image_version}.qcow2")
        build_architecture(architecture_path, self.images_dir, False)
        assert exists(self.image)

        self.node_options_path = join(
            "tests", "smoke", "res", "node_options", f"{self.architecture}.json"
        )
        assert exists(self.node_options_path)
        self.init_done = True

    # Should be used by the non async function tearDownClass to ensure that
    # the following cleanup is done before the class is destroyed
    def tearDown(self):
        assert fs_remove(self.images_dir, recursive=True)
