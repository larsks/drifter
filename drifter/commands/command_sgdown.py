#!/usr/bin/python

import os
import sys

from ..command import Command

class CommandSgdown (Command):
    def build_subparser(self):
        p = self.parser.add_parser('sgdown',
                help='Delete all security groups.')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        api.delete_security_groups()

