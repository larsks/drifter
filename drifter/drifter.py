#!/usr/bin/python

import os
import sys
import pprint
import logging
import time
from multiprocessing import Process, Lock
from itertools import count

import jinja2
import yaml

from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import novaclient.v1_1.client

from instance import Instance
from secgroups import Rule
from decorators import *

DEFAULT_USER_CONFIG = os.path.join(os.environ['HOME'], '.drifter.yml')
DEFAULT_PROJECT_CONFIG = 'project.yml'

cache_opts = {
    'cache.type': 'file',
    'cache.data_dir': '.drifter/cache/data',
    'cache.lock_dir': '.drifter/cache/lock'
}

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
        self.setup_cache()
        self.setup_locks()
        self.create_client()

    def setup_locks(self):
        '''Create locks used for synchronizing parallel
        execution (e.g. when creating instances).'''
        self.net_lock = Lock()

    def setup_logging(self):
        '''Create a logger for this Drifter instance.'''
        self.log = logging.getLogger('drifter')

    def setup_cache(self):
        '''Set up a beaker cache manager.'''
        self.cachemgr = CacheManager(**parse_cache_config_options(cache_opts))
        self.image_cache = self.cachemgr.get_cache('images', expires=1800)
        self.flavor_cache = self.cachemgr.get_cache('flavors', expires=1800)

    def qualify(self, name):
        '''Return <os_username>.<project_name>.<name> given <name>.'''
        return '%s.%s.%s' % (
                self.config['os_username'],
                self.config['project_name'],
                name,
                )

    def instances(self):
        '''This is a generate that yields drifter.instance.Instance objects
        for each instance in your drifter configuration.'''

        defaults = self.config['instances'].get('default', {})
        for name, config in self.config['instances'].items():
            if name == 'default':
                continue
            if config is None:
                config = {}

            yield Instance(self, name, config, defaults)

    def create_client(self):
        '''Creates a novaclient.v1_1.client.Client for this
        Drifter instance.'''

        self.client = novaclient.v1_1.client.Client(
                self.config['os_username'],
                self.config['os_password'],
                self.config['os_tenant_name'],
                self.config['os_auth_url'],
                service_type="compute")

    def load_config(self, path):
        '''Load a YAML configuration file.  The file is first parsed
        by the Jinja2 templat engine and then passed to the YAML
        parser.
        
        Returns the result of yaml.load()'''

        self.log.info('loading configuration from %s', path)
        with open(path) as fd:
            tmpl = jinja2.Template(fd.read())

        return yaml.load(tmpl.render())

    def load_user_config(self):
        '''Load configuration from user_config_file (generally
        ~/.drifter.yml).'''

        self.config = self.load_config(self.user_config_file)['drifter']

    def load_project_config(self):
        '''Load configuration from project_config_file (generally
        ./project.yml).'''

        self.config.update(self.load_config(self.project_config_file)['project'])

    @ratelimit
    def create_security_group(self, name):
        '''Given <name>, either create and return a new security group
        named <name> or return the existing security group with the same
        name.'''

        self.log.info('creating security group %s', self.qualify(name))
        try:
            group = self.client.security_groups.find(name=self.qualify(name))
        except novaclient.exceptions.NotFound:
            group = self.client.security_groups.create(
                    self.qualify(name),
                    '%s security group' % name)

        return group

    @ratelimit
    def create_security_group_rule(self, group, rule):
            try:
                sr = self.client.security_group_rules.create(
                        group.id,
                        ip_protocol=rule['protocol'],
                        from_port=rule['from port'],
                        to_port=rule['to port'])
            except novaclient.exceptions.BadRequest:
                # This probably means that the rule already exists.
                pass

    def create_security_group_rules(self, group, rules):
        '''Provision security group <group> with rules from <rules>'''

        self.log.info('adding rules to security group %s', group.name)
        for rule in rules:
            rule = Rule(rule)
            self.create_security_group_rule(self, group, rule)


    def create_security_groups(self):
        '''Create and provision all security groups defined in the
        configuration.'''

        for name, rules in self.config['security groups'].items():
            group = self.create_security_group(name)
            self.create_security_group_rules(group, rules)

    def delete_security_group(self, name):
        '''Delete the named security group.  If it does not exist, ignore
        the error.'''
        self.log.info('deleting security group %s', self.qualify(name))
        try:
            group = self.client.security_groups.find(name=self.qualify(name))
            self.client.security_groups.delete(group.id)
        except novaclient.exceptions.NotFound:
            pass

    def delete_security_groups(self):
        '''Delete all security groups defined in the configuration.'''
        for name, rules in self.config['security groups'].items():
            self.delete_security_group(name)

    def create_instance(self, instance):
        '''Create an instance and assign an ip address.'''
        
        self.create_client()

        # Don't try to create instances that
        # have already booted.
        if instance.status != 'down':
            self.log.warn('ignore create request -- this instance is not down')
            return

        instance.create()
        instance.assign_ip()

    def create_instances(self):
        '''Create all instances defined in the configuration.'''
        defaults = self.config['instances'].get('default', {})

        tasks = []
        for instance in self.instances():
            t = Process(
                    target=self.create_instance,
                    args=(instance,),
                    name='create-%(name)s' % instance)
            t.start()
            tasks.append(t)

        self.log.debug('waiting for tasks')
        while tasks:
            tasks[0].join()
            t = tasks.pop(0)
            self.log.debug('task %s completed', t)

    def delete_instance(self, instance):
        '''Delete a single instance.'''
        instance.delete()

    def delete_instances(self):
        '''Delete all instances defined in the configuration.'''
        defaults = self.config['instances'].get('default', {})

        for instance in self.instances():
            self.delete_instance(instance)

    def find_image(self, image):
        def _find_image():
            return self.client.images.find(name=image).id
        id = self.image_cache.get(key=image, createfunc=_find_image)
        self.log.debug('got id=%s for image=%s', id, image)
        return self.client.images.get(id)

    def find_flavor(self, flavor):
        def _find_flavor():
            return self.client.flavors.find(name=flavor).id
        id = self.flavor_cache.get(key=flavor, createfunc=_find_flavor)
        self.log.debug('got id=%s for flavor=%s', id, flavor)
        return self.client.flavors.get(id)

    def all_up(self):
        '''Return True if all instances are active.'''
        return all(i.status == 'active' for i in self.instances())

    def all_down(self):
        '''Return True if all instances are down.'''
        return all(i.status == 'down' for i in self.instances())

    def wait_for_up(self):
        '''Wait for all instances to become active.'''
        self.log.info('waiting for instances to start')
        while not self.all_up():
            time.sleep(1)
        self.log.info('instances are started')

    def wait_for_down(self):
        '''Wait for all instances to become down.'''
        self.log.info('waiting for instances to stop')
        while not self.all_down():
            time.sleep(1)
        self.log.info('instances are down')

    def check(self):
        '''Return a (name, status) tuple for all instances defined
        in the configuration.'''
        return [(x['name'], x.status) for x in self.instances()]

if __name__ == '__main__':
    logging.basicConfig(
            level = logging.DEBUG,
            format='%(asctime)s %(name)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            )

    d = Drifter()

