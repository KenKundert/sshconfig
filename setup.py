#!/usr/bin/env python

from codecs import open

from setuptools import setup

with open("README.rst", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="sshconfig",
    version="1.3.2",
    author="Ken Kundert",
    author_email="sshconfig@nurdletech.com",
    description="SSH config file generator",
    long_description=readme,
    url="https://sshconfig.readthedocs.io",
    download_url="https://github.com/kenkundert/sshconfig/tarball/master",
    license="GPLv3+",
    packages="sshconfig".split(),
    entry_points={"console_scripts": ["sshconfig=sshconfig.main:main"]},
    install_requires="appdirs arrow docopt inform shlib".split(),
    python_requires=">=3.6",
    keywords="ssh".split(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
)
