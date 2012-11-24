#!/usr/bin/python

import os
import sys

from ..command import Command

class CommandSgup (Command):
    def build_subparser(self):
        p = self.parser.add_parser('sgup',
                help='Create all security groups.')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        api.create_security_groups()

