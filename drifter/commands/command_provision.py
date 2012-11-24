#!/usr/bin/python

import os
import sys
import subprocess

from ..command import Command
import command_ansible_hosts

def find_binary(name):
    for dir in os.environ['PATH'].split(':'):
        fullpath = os.path.join(dir, name)
        if os.path.exists(fullpath):
            return fullpath

class CommandProvision (Command):
    def build_subparser(self):
        p = self.parser.add_parser('provision')
        p.add_argument('--verbose', '-v', action='store_true')
        p.add_argument('--sudo', '-s', action='store_true')
        p.add_argument('--remote-user', '-u')
        p.add_argument('--extra-vars', '-e')
        p.set_defaults(handler=self.run)

    def handler(self, api, opts):
        if not os.path.exists('playbook.yml'):
            self.log.error('your project does not have a playbook')
            sys.exit(1)

        with open('.ansible_hosts', 'w') as fd:
            self.log.debug('writing ansible hosts to .ansible_hosts')
            command_ansible_hosts.gen_ansible_hosts(api, fd)

        playbook_args = []
        if opts.verbose:
            playbook_args.append('-v')
        if opts.sudo:
            playbook_args.append('-s')
        if opts.remote_user:
            playbook_args.append('-u')
            playbook_args.append(opts.remote_user)
        if opts.extra_vars:
            playbook_args.append('-e')
            playbook_args.append(opts.extra_vars)

        self.log.info('calling ansible-playbook')
        subprocess.call(
                [
                    'ansible-playbook',
                    '-i', '.ansible_hosts',
                    ]
                + playbook_args
                + ['playbook.yml']
                )

