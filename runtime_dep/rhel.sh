#!/bin/bash

dnf install libvirt qemu-kvm
dnf --enablerepo=crb install libvirt-devel