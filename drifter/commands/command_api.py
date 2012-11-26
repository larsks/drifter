#!/usr/bin/python

import os
import sys
import code

from ..command import Command

banner = '''
Drifter object available as "api".

- api.client -- a novaclient.v1_1.client.Client object
- api.config -- configuration read from project.yml and
  ~/.drifter.yml
- api.instances -- a generator returning a
  drifter.instance.Instance object for each instance in your
  configuration.
'''

class CommandApi (Command):
    def build_subparser(self):
        p = self.parser.add_parser('api',
                help='Start an interactive Python shell with access to the Drifter API.')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        try:
            import readline
        except ImportError:
            pass

        c = code.InteractiveConsole({
            '__name__': '__drifter__',
            'api': api,
            })
        c.interact(banner)

