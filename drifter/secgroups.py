#!/usr/bin/python

import os
import sys

class Rule (dict):
    __defaults__ = {
            'protocol': 'tcp',
            'from port': '-1',
            'to port': '-1',
            'source': '0.0.0.0/0',
            }

    def __getitem__(self, k):
        try:
            return super(Rule, self).__getitem__(k)
        except KeyError:
            if k == 'to port':
                return self['from port']
            else:
                return self.__defaults__[k]

    def __str__(self):
        return '<Rule %(protocol)s ports ' \
                '%(from port)s:%(to port)s ' \
                'from %(source)s>' % self

    def __repr__(self):
        return str(self)
