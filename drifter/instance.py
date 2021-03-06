#!/usr/bin/python

import os
import sys
import logging
import time

import jinja2

import novaclient.exceptions

from decorators import *

class Instance (dict):
    def __init__ (self, project, name, cfg, parent):
        super(Instance, self).__init__(cfg)
        self['name'] = name
        self.parent = parent
        self.project = project
        self.net_lock = project.net_lock
        self.log = logging.getLogger('drifter.instance.%s' % self['name'])
        
        self.cache = self.project.cachemgr.get_cache(
                'instance/%s' % self['name'], expire=300)

    def __getitem__ (self, k):
        try:
            return super(Instance, self).__getitem__(k)
        except KeyError:
            return self.parent[k]

    def __contains__ (self, k):
        return any([
                super(Instance, self).__contains__(k),
                self.parent.__contains__(k),
                ])

    def __str__(self):
        return '<Instance %(name)s f:%(flavor)s i:%(image)s>' % self

    def __repr__(self):
        return str(self)

    @ratelimit
    @synchronized('net_lock')
    def assign_ip(self):
        '''Find an available floating ip and assign it to
        the instance.'''
        # Wait until a fixed address is available.
        self.log.info('waiting for a fixed ip address')
        while not self.server.networks:
            time.sleep(0.5)

        self.log.info('assigning floating ip address')
        available = [
                ip for ip in self.project.client.floating_ips.list()
                if ip.instance_id is None ]

        if available:
            ip = available[0]
            self.log.info('found available ip %s', ip)
        else:
            ip = self.project.client.floating_ips.create()
            self.log.info('allocated new ip %s', ip)

        self.server.add_floating_ip(ip.ip)

    @ratelimit
    def create(self):
        '''Boot the instance.'''

        self.log.info('creating')
        self.cache.clear()

        image = self.project.find_image(self['image'])
        self.log.debug('got image')
        flavor = self.project.find_flavor(self['flavor'])
        self.log.debug('got flavor')
        security_groups = [self.project.qualify(x) for x in
                self['security groups']]

        key_name = self.project.config.get('key_name')

        self.project.client.servers.create(
               self.project.qualify(self['name']),
               image,
               flavor,
               security_groups=security_groups,
               userdata=self.userdata,
               key_name=key_name,
               )

    def delete(self):
        '''Delete the instance.'''
        self.log.info('deleting')
        self.cache.clear()

        try:
            self.server.delete()
        except novaclient.exceptions.NotFound:
            pass

    @property
    def id(self):
        '''Return the server UUID.'''
        def get_id():
            self.log.debug('getting id from remote api')
            srvr = self.project.client.servers.find(
                    name=self.project.qualify(self['name']))
            id = srvr.id
            self.log.debug('got id=%s', id)
            return id

        return self.cache.get(key='id', createfunc=get_id)

    @property
    def server(self):
        '''Return the Nova API server object for this instance.'''
        srvr = self.project.client.servers.get(self.id)
        return srvr

    @property
    def status(self):
        '''Return the status of this instance.  'down' if not booted, 
        otherwise whatever the Nova status() method returns.'''
        try:
            return self.server.status.lower()
        except novaclient.exceptions.NotFound:
            return 'down'

    @property
    def is_down(self):
        '''Returns True if this instance is down, False otherwise.'''
        return self.status == 'down'

    @property
    def is_up(self):
        '''Returns True if this instance is active, False otherwise.'''
        return self.status == 'active'

    @property
    def ip(self):
        '''Returns the (a) floating ip assigned to this instance.'''
        def get_ip():
            self.log.debug('getting ip from remote api')
            for fip in  self.project.client.floating_ips.list():
                if fip.instance_id == self.server.id:
                    return fip.ip

        return self.cache.get(key='ip', createfunc=get_ip)

    @property
    def userdata(self):
        if 'userdata' in self:
            self.log.debug('reading userdata from %s', self['userdata'])
            tmpl = jinja2.Template(open(self['userdata']).read())
            data = tmpl.render(
                    project=self.project,
                    instance=self,
                    )
            return data
        else:
            return None

