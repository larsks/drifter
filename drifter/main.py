#!/usr/bin/python

import os
import sys
import argparse
import logging
import pprint

import novaclient.v1_1
import novaclient.exceptions

from drifter import Drifter

from commands.command_up import CommandUp
from commands.command_down import CommandDown
from commands.command_status import CommandStatus
from commands.command_sgup import CommandSgup
from commands.command_sgdown import CommandSgdown
from commands.command_hosts import CommandHosts
from commands.command_ansible_hosts import CommandAnsibleHosts

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--user-config-file', '--config', '-f')
    p.add_argument('--project-config-file')
    p.add_argument('--verbose', '-v',
            action='store_true')
    p.add_argument('--debug',
            action='store_true')

    subparsers = p.add_subparsers(title='Available commands')

    CommandUp(subparsers)
    CommandDown(subparsers)
    CommandHosts(subparsers)
    CommandAnsibleHosts(subparsers)
    CommandStatus(subparsers)
    CommandSgup(subparsers)
    CommandSgdown(subparsers)

    return p.parse_args()

def main():
    global api
    opts = parse_args()

    logging.basicConfig(
            level = logging.DEBUG if opts.debug \
                    else logging.INFO if opts.verbose \
                    else logging.WARN,
                    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )

    api = Drifter(
            user_config_file=opts.user_config_file,
            project_config_file=opts.project_config_file)
    opts.handler(api, opts)

if __name__ == '__main__':
    main()

