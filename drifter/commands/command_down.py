#!/usr/bin/python

import os
import sys

from command import Command

class CommandDown (Command):
    def build_subparser(self):
        p = self.parser.add_parser('down')
        p.add_argument('server', nargs='?')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        api.delete_instances()
        api.wait_for_down()
        api.delete_security_groups()


