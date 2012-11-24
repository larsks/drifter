#!/usr/bin/python

import os
import sys

from ..command import Command

class CommandUp (Command):
    def build_subparser(self):
        p = self.parser.add_parser('up',
                help='Start all instances.')
        p.add_argument('server', nargs='?')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        print 'Creating all security groups.'
        api.create_security_groups()
        print 'Creating all instances.'
        api.create_instances()
        print 'Waiting for instances to become active.'
        api.wait_for_up()

