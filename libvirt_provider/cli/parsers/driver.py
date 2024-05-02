def valid_driver_group(parser):
    driver_group(parser)


def driver_group(
    parser,
    default_driver_name="libvirt",
    default_driver_uri="qemu:///session",
    default_driver_key=None,
    default_driver_secret=None,
):
    driver_group = parser.add_argument_group(title="Driver arguments")
    driver_group.add_argument("--driver-name", default=default_driver_name)
    driver_group.add_argument("--driver-uri", default=default_driver_uri)
    driver_group.add_argument("--driver-key", default=default_driver_key)
    driver_group.add_argument("--driver-secret", default=default_driver_secret)


def add_driver_group(
    parser,
    default_driver_name="libvirt",
    default_driver_uri="qemu:///session",
    default_driver_key=None,
    default_driver_secret=None,
):
    driver_group(
        parser,
        default_driver_name=default_driver_name,
        default_driver_uri=default_driver_uri,
        default_driver_key=default_driver_key,
        default_driver_secret=default_driver_secret,
    )
