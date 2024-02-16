def valid_driver_group(parser):
    driver_group(parser)


def driver_group(parser):
    driver_group = parser.add_argument_group(title="Driver arguments")
    driver_group.add_argument("--driver-uri", default="")
    driver_group.add_argument("--driver-key", default=None)
    driver_group.add_argument("--driver-secret", default=None)

    # HACK to extract the set provider from the cli
    # driver_group.add_argument("--libvirt", action="store_true", default=True)
