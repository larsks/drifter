#!/usr/bin/python

import os
import sys

from ..command import Command

class CommandHosts (Command):
    def build_subparser(self):
        p = self.parser.add_parser('hosts',
                help='Output a list of hosts in /etc/hosts format.')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        if not api.all_up() and not opts.force:
            self.log.error('some instances are not up (use --force to ' \
                    'continue anyay)')
            sys.exit(1)

        for instance in api.instances():
            print instance.ip, instance['name']

