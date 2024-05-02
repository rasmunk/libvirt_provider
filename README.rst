================
libvirt_provider
================

A libvirt orchestration plugin for `corc <https://github.com/rasmunk/corc>`_

------------
Installation
------------

.. code-block:: bash

    pip install libvirt-provider

------------
Dependencies
------------

Before the ``libvirt-provider`` can be succesfully installed, the distribution associated dependency script
in the ``devel_dep`` folder should be executed. This will install the nessesary library files that ``libvirt-provider``
require to function properly.

In addition, before an actual resource such as an instance or a container can be created by ``libvirt-provider``,
the required ``libvirt`` daemon has to be running on the system. This can be installed via the distribution installer
scripts in the ``runtime_dep`` folder.

-----
Usage
-----

The libvirt-provider plugin can be used on its own to orchestrate libvirt resources.
Currently it supports orchestrating virtual machines and containers.
These resources can be orchestrated via the CLI interface::

    $ libvirt-provider -h
    usage: libvirt_provider [-h] {instance,container} ...

    options:
    -h, --help            show this help message and exit

    COMMAND:
    {instance,container}

For instance, to orchestrate an instance, the following command can be used::

    $ usage: libvirt_provider instance create [-h]
    [-dt INSTANCE_DOMAIN_TYPE] [-ddtype INSTANCE_DISK_DEVICE_TYPE] [-ddn INSTANCE_DISK_DRIVER_NAME]
    [-ddt INSTANCE_DISK_DRIVER_TYPE] [-dtd INSTANCE_DISK_TARGET_DEV] [-dtb INSTANCE_DISK_TARGET_BUS]
    [-memory INSTANCE_MEMORY_SIZE] [-vcpus INSTANCE_NUM_VCPUS] [-cpu-arch INSTANCE_CPU_ARCHITECTURE]
    [-cpu-mode INSTANCE_CPU_MODE] [-mach INSTANCE_MACHINE] [-ct INSTANCE_CONSOLE_TYPE] [-st INSTANCE_SERIAL_TYPE]
    [-sttp INSTANCE_SERIAL_TYPE_TARGET_PORT] [-tp INSTANCE_TEMPLATE_PATH]
    name disk_image_path

    optional arguments:
    -h, --help            show this help message and exit

    Instance create arguments:
    name                  The name of the instance
    disk_image_path       The path to the disk image
    -dt INSTANCE_DOMAIN_TYPE, --domain-type INSTANCE_DOMAIN_TYPE
                            The domain type
    -ddtype INSTANCE_DISK_DEVICE_TYPE, --disk-device-type INSTANCE_DISK_DEVICE_TYPE
                            The disk type
    -ddn INSTANCE_DISK_DRIVER_NAME, --disk-driver-name INSTANCE_DISK_DRIVER_NAME
                            The disk driver name
    -ddt INSTANCE_DISK_DRIVER_TYPE, --disk-driver-type INSTANCE_DISK_DRIVER_TYPE
                            The disk driver type
    -dtd INSTANCE_DISK_TARGET_DEV, --disk-target-dev INSTANCE_DISK_TARGET_DEV
                            The disk target device
    -dtb INSTANCE_DISK_TARGET_BUS, --disk-target-bus INSTANCE_DISK_TARGET_BUS
                            The disk target bus
    -memory INSTANCE_MEMORY_SIZE, --memory-size INSTANCE_MEMORY_SIZE
                            The memory size of the instance, interpreted as KiB. Default is 1024MiB.
    -vcpus INSTANCE_NUM_VCPUS, --num-vcpus INSTANCE_NUM_VCPUS
                            The number of virtual CPUs
    -cpu-arch INSTANCE_CPU_ARCHITECTURE, --cpu-architecture INSTANCE_CPU_ARCHITECTURE
                            The CPU architecture
    -cpu-mode INSTANCE_CPU_MODE, --cpu-mode INSTANCE_CPU_MODE
                            The CPU mode to be used when running the instance
    -mach INSTANCE_MACHINE, --machine INSTANCE_MACHINE
                            The machine type
    -ct INSTANCE_CONSOLE_TYPE, --console-type INSTANCE_CONSOLE_TYPE
                            The console type
    -st INSTANCE_SERIAL_TYPE, --serial-type INSTANCE_SERIAL_TYPE
                            The serial type
    -sttp INSTANCE_SERIAL_TYPE_TARGET_PORT, --serial-type-target-port INSTANCE_SERIAL_TYPE_TARGET_PORT
                            The serial type target port
    -tp INSTANCE_TEMPLATE_PATH, --template-path INSTANCE_TEMPLATE_PATH
                            The path to the XML template that should be used to create the instance.


As indicated by the instance creation command, the ``libvirt-provider`` expects that a disk image file is provided as an argument::

    $ libvirt-provider instance create <name> <disk-image-file>

The <disk-image-file> can either be prepared by downloading directly from one of the distribution repositories, or a prepared with a tool
like our `gen-vm-image <https://github.com/ucphhpc/gen-vm-image>`_ before it is used to create an instance via ``libvirt-provider``.

In turn, an orchestrated instance can be removed via the ``remove`` argument::

    $ libvirt-provider instance remove <instance-id>

To discover the <instance-id> of a particular instance, the ``list`` argument can be used::

    $ libvirt-provider instance ls
    {
        "instances": [],
        "msg": "Instances",
        "status": "success"
    }

