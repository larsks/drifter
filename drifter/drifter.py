#!/usr/bin/python

import os
import sys
import pprint
import logging
import time

import jinja2
import yaml

import novaclient.v1_1.client

from instance import Instance
from secgroups import Rule

DEFAULT_USER_CONFIG = os.path.join(os.environ['HOME'], '.drifter.yml')
DEFAULT_PROJECT_CONFIG = 'project.yml'

class Drifter (object):
    def __init__ (self,
            user_config_file=None,
            project_config_file=None):

        self.user_config_file = user_config_file \
                if user_config_file \
                else DEFAULT_USER_CONFIG
        self.project_config_file = project_config_file \
                if project_config_file \
                else DEFAULT_PROJECT_CONFIG

        self.setup_logging()
        self.load_user_config()
        self.load_project_config()
        self.create_client()

    def setup_logging(self):
        self.log = logging.getLogger('drifter')

    def qualify(self, name):
        return '%s.%s.%s' % (
                self.config['os_username'],
                self.config['project_name'],
                name,
                )

    def instances(self):
        defaults = self.config['instances'].get('default', {})
        for name, config in self.config['instances'].items():
            if name == 'default':
                continue
            if config is None:
                config = {}

            yield Instance(self, name, config, defaults)

    def create_client(self):
        self.client = novaclient.v1_1.client.Client(
                self.config['os_username'],
                self.config['os_password'],
                self.config['os_tenant_name'],
                self.config['os_auth_url'],
                service_type="compute")

    def load_config(self, path):
        self.log.info('loading configuration from %s', path)
        with open(path) as fd:
            tmpl = jinja2.Template(fd.read())

        return yaml.load(tmpl.render())

    def load_user_config(self):
        self.config = self.load_config(self.user_config_file)['drifter']

    def load_project_config(self):
        self.config.update(self.load_config(self.project_config_file)['project'])

    def create_security_group(self, name):
        self.log.info('creating security group %s', self.qualify(name))
        try:
            group = self.client.security_groups.find(name=self.qualify(name))
        except novaclient.exceptions.NotFound:
            group = self.client.security_groups.create(
                    self.qualify(name),
                    '%s security group' % name)

        return group

    def create_security_group_rules(self, group, rules):
        self.log.info('adding rules to security group %s', group.name)
        for rule in rules:
            self.log.debug('adding rule (pre) %s', rule)
            rule = Rule(rule)
            self.log.debug('adding rule (post) %s', rule)

            try:
                sr = self.client.security_group_rules.create(
                        group.id,
                        ip_protocol=rule['protocol'],
                        from_port=rule['from port'],
                        to_port=rule['to port'])
            except novaclient.exceptions.BadRequest:
                # This probably means that the rule already exists.
                pass

    def create_security_groups(self):
        for name, rules in self.config['security groups'].items():
            group = self.create_security_group(name)
            self.create_security_group_rules(group, rules)

    def delete_security_group(self, name):
        self.log.info('deleting security group %s', self.qualify(name))
        try:
            group = self.client.security_groups.find(name=self.qualify(name))
            self.client.security_groups.delete(group.id)
        except novaclient.exceptions.NotFound:
            pass

    def delete_security_groups(self):
        for name, rules in self.config['security groups'].items():
            self.delete_security_group(name)

    def create_instance(self, instance):
        instance.create()
        instance.assign_ip()

    def create_instances(self):
        defaults = self.config['instances'].get('default', {})

        for instance in self.instances():
            if instance.is_down:
                self.create_instance(instance)

    def delete_instance(self, instance):
        instance.delete()

    def delete_instances(self):
        defaults = self.config['instances'].get('default', {})

        for instance in self.instances():
            self.delete_instance(instance)

    def all_up(self):
        return all(i.status == 'active' for i in self.instances())

    def all_down(self):
        return all(i.status == 'down' for i in self.instances())

    def wait_for_up(self):
        self.log.info('waiting for instances to start')
        while not self.all_up():
            time.sleep(1)
        self.log.info('instances are started')

    def wait_for_down(self):
        self.log.info('waiting for instances to stop')
        while not self.all_down():
            time.sleep(1)
        self.log.info('instances are down')

    def check(self):
        return [(x['name'], x.status) for x in self.instances()]

if __name__ == '__main__':
    logging.basicConfig(
            level = logging.DEBUG,
            format='%(asctime)s %(name)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            )

    d = Drifter()

