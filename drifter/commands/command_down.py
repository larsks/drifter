#!/usr/bin/python

import os
import sys

from ..command import Command

class CommandDown (Command):
    def build_subparser(self):
        p = self.parser.add_parser('down',
                help='Shut down all instances.')
        p.add_argument('server', nargs='?')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        print 'Deleting all instances.'
        api.delete_instances()
        print 'Waiting for instances to stop.'
        api.wait_for_down()
        api.delete_security_groups()


