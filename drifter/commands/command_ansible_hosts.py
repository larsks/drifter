#!/usr/bin/python

import os
import sys
import json

from command import Command

class CommandAnsibleHosts (Command):
    def build_subparser(self):
        p = self.parser.add_parser('ansible_hosts')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        systems = []
        for i in api.instances():
            systems.append('%s ansible_ssh_ip=%s' % (i['name'], i.ip))

        print json.dumps({
                api.config['project_name']: systems
                }, indent=True)

