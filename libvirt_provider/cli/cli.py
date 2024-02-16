import argparse



def functions_cli(parser):
    parser.add_parser("create", help="Create a new VM")
    parser.add_parser("remove", help="Remove a VM")
    parser.add_parser("start", help="Start a VM")
    parser.add_parser("stop", help="Stop a VM")
    parser.add_parser("list", help="List all VMs")
    parser.add_parser("state", help="Get the state of a VM")


def run():
    parser = argparse.ArgumentParser(description="Libvirt provider")
    functions_cli(parser)
    arguments = parser.parse_args()
    return arguments



if __name__ == "__main__":
    arguments = run()