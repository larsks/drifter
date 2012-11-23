#!/usr/bin/python

import os
import sys

from command import Command

class CommandStatus (Command):
    def build_subparser(self):
        p = self.parser.add_parser('status')
        p.add_argument('server', nargs='?')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        for name, status in api.check():
            print name, status

