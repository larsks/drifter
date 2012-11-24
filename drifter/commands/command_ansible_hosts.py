#!/usr/bin/python

import os
import sys
import json

from ..command import Command

class CommandAnsibleHosts (Command):
    def build_subparser(self):
        p = self.parser.add_parser('ansible_hosts')
        p.add_argument('--host')
        p.add_argument('--list', action='store_true')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        systems = {api.config['project_name']: []}
        for i in api.instances():
            systems[api.config['project_name']].append('%s' % (i.ip))
            systems[i['name']] = [i.ip]

        if opts.host:
            print json.dumps({})
        else:
            print json.dumps(systems, indent=True)

