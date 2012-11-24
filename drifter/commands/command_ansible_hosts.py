#!/usr/bin/python

import os
import sys
import json

import novaclient.exceptions

from ..command import Command

def gen_ansible_hosts(api, out):
    for i in api.instances():
        try:
            print >>out, '%s ansible_ssh_host=%s' % (
                    i['name'], i.ip
                    )
        except novaclient.exceptions.NotFound:
            continue

class CommandAnsibleHosts (Command):
    def build_subparser(self):
        p = self.parser.add_parser('ansible_hosts',
                help='Generate output suitable for use as an Ansible inventory.')
        p.add_argument('--host')
        p.add_argument('--list', action='store_true')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        if not api.all_up() and not opts.force:
            self.log.error('some instances are not up (use --force to ' \
                    'continue anyay)')
            sys.exit(1)

        gen_ansible_hosts(api, sys.stdout)

