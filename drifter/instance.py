#!/usr/bin/python

import os
import sys
import logging
import time

import novaclient.exceptions

class Instance (dict):
    def __init__ (self, project, name, cfg, parent):
        super(Instance, self).__init__(cfg)
        self['name'] = name
        self.parent = parent
        self.project = project
        self.log = logging.getLogger('drifter.instance.%s' % self['name'])

    def __getitem__ (self, k):
        try:
            return super(Instance, self).__getitem__(k)
        except KeyError:
            return self.parent[k]

    def __str__(self):
        return '<Instance %(name)s f:%(flavor)s i:%(image)s>' % self

    def __repr__(self):
        return str(self)

    def assign_ip(self):
        # Wait until a fixed address is available.
        while not self.server.networks:
            time.sleep(0.5)

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

    def create(self):
        self.log.info('creating')

        image = self.project.client.images.find(name=self['image'])
        flavor = self.project.client.flavors.find(name=self['flavor'])
        security_groups = [self.project.qualify(x) for x in
                self['security_groups']]

        if 'userdata' in self:
            userdata = open(self['userdata']).read()
        else:
            userdata = None

        key_name = self.project.config.get('key_name')

        self.project.client.servers.create(
               self.project.qualify(self['name']),
               image,
               flavor,
               security_groups=security_groups,
               userdata=userdata,
               key_name=key_name,
               )

    def delete(self):
        self.log.info('deleting')

        try:
            self.server.delete()
        except novaclient.exceptions.NotFound:
            pass

    @property
    def server(self):
        srvr = self.project.client.servers.find(
                name=self.project.qualify(self['name']))
        return srvr

    @property
    def status(self):
        try:
            return self.server.status.lower()
        except novaclient.exceptions.NotFound:
            return 'down'

    @property
    def is_down(self):
        return self.status == 'down'

    @property
    def is_up(self):
        return self.status == 'active'

    @property
    def ip(self):
        for fip in  self.project.client.floating_ips.list():
            if fip.instance_id == self.server.id:
                return fip.ip


