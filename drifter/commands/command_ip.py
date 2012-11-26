#!/usr/bin/python

import os
import sys

from ..command import Command

class CommandIp (Command):
    def build_subparser(self):
        p = self.parser.add_parser('ip',
                help='Output the ip address of a named instance.')
        p.add_argument('name')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        for instance in api.instances():
            if instance['name'] == opts.name:
                print instance.ip

