#!/usr/bin/python

import os
import sys
import json

from ..command import Command

def gen_ansible_hosts(api, out):
        for i in api.instances():
            print >>out, '%s ansible_ssh_host=%s' % (
                    i['name'], i.ip
                    )

class CommandAnsibleHosts (Command):
    def build_subparser(self):
        p = self.parser.add_parser('ansible_hosts')
        p.add_argument('--host')
        p.add_argument('--list', action='store_true')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        gen_ansible_hosts(api, sys.stdout)

