#!/usr/bin/python

import os
import sys
import time
import logging
from types import MethodType
from itertools import count
from functools import wraps

import novaclient.exceptions

class ratelimit (object):
    '''Handles retring Nova API calls that fail due to API rate limits.'''

    def __init__(self, f):
        self.f = f
        self.__name__ = f.__name__
        self.__doc__ = f.__doc__

        self.log = logging.getLogger('drifter.func.%s' % f.__name__)

    # From:
    # http://www.outofwhatbox.com/blog/2010/07/python-decorating-with-class/
    def __get__(self, obj, ownerClass=None):
        # Return a wrapper that binds self as a method of obj
        return MethodType(self, obj)

    def __call__(self, *args, **kwargs):
        for i in count(1):
            try:
                return self.f(*args, **kwargs)
            except novaclient.exceptions.OverLimit:
                # Exponential backoff with a max wait of 30 seconds.
                wait = min(30, 2*i)
                self.log.warn('api rate overlimit (retry in %d)', 
                        wait)
                time.sleep(wait)

class synchronized (object):
    def __init__ (self, lockname):
        self.lockname = lockname
        self.log = logging.getLogger('drifter.lock.%s' % lockname)

    def __call__(self, f):
        @wraps(f)
        def _(other,*args, **kwargs):
            lock = other.__getattribute__(self.lockname)
            self.log.debug('waiting for lock')
            lock.acquire()
            self.log.debug('acquired lock')
            try:
                return f(other, *args, **kwargs)
            finally:
                self.log.debug('releasing lock')
                lock.release()
        return _

