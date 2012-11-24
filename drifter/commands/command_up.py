#!/usr/bin/python

import os
import sys

from ..command import Command

class CommandUp (Command):
    def build_subparser(self):
        p = self.parser.add_parser('up')
        p.add_argument('server', nargs='?')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        api.create_security_groups()
        api.create_instances()
        api.wait_for_up()

