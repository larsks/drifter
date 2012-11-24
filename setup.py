#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'drifter',
    description = 'Provision instances in OpenStack',
    long_description = open('README.md').read(),
    author = 'Lars Kellogg-Stedman',
    author_email = 'lars@oddbit.com',
    version = "1.00",
    packages = find_packages(),
    install_requires = open('requirements.txt').readlines(),
    entry_points = {
        'console_scripts': [
            'drifter = drifter.main:main',
            'drifter-ansible-hosts = drifter.main:cmd_ansible_hosts',
            ],
        },
)

