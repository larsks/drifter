#!/usr/bin/python

import os
import sys

from ..command import Command

class CommandHosts (Command):
    def build_subparser(self):
        p = self.parser.add_parser('hosts')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        for instance in api.instances():
            print instance.ip, instance['name']

