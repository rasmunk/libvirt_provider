#!/usr/bin/python
# coding: utf-8
import os
from setuptools import setup, find_packages

cur_dir = os.path.abspath(os.path.dirname(__file__))


def read(path):
    with open(path, "r") as _file:
        return _file.read()


def read_req(name):
    path = os.path.join(cur_dir, name)
    return [req.strip() for req in read(path).splitlines() if req.strip()]


version_ns = {}
with open(os.path.join(cur_dir, "version.py")) as f:
    exec(f.read(), {}, version_ns)


long_description = open("README.rst").read()
setup(
    name="libvirt_provider",
    version=version_ns["__version__"],
    description="A corc plugin for a libvirt orchestration provider",
    long_description=long_description,
    author="Rasmus Munk",
    author_email="munk1@live.dk",
    packages=find_packages(),
    url="https://github.com/rasmunk/libvirt_provider",
    license="MIT",
    keywords=["Orchstration", "Virtual Machine"],
    install_requires=read_req("requirements.txt"),
    extras_require={
        "test": read_req("tests/requirements.txt"),
        "dev": read_req("requirements-dev.txt"),
    },
    # Ensures that the plugin can be discovered/loaded by corc
    entry_points={
        "console_scripts": ["libvirt-provider = libvirt_provider.cli.cli:run"],
        "corc.plugins": ["libvirt_provider=libvirt_provider.instance"],
        "corc.plugins.orchestration": ["libvirt_provider=libvirt_provider.instance"],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
