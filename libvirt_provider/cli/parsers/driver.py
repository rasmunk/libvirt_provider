def valid_driver_group(parser):
    driver_group(parser)


def driver_group(parser):
    driver_group = parser.add_argument_group(title="Driver arguments")
    driver_group.add_argument("--driver-name", default="libvirt")
    driver_group.add_argument("--driver-uri", default="qemu:///session")
    driver_group.add_argument("--driver-key", default=None)
    driver_group.add_argument("--driver-secret", default=None)
