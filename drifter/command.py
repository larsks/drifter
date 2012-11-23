#!/usr/bin/python

import os
import sys
import logging
import argparse

class Command (object):
    def __init__ (self, parser):
        self.parser = parser
        self.build_subparser()

    def build_subparser(self):
        raise NotImplementedError()

    def run(self, api, opts):
        self.log = logging.getLogger(
                'drifter.command.%s' % self.__class__.__name__)
        self.handler(api, opts)

