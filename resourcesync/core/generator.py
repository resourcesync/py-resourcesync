# -*- coding: utf-8 -*-

"""
:samp:`The Generator base class.`
"""

import attr
from attr.validators import instance_of, optional

#import resourcesync.parameters.parameters as parameters
import resourcesync.rsxml.rsxml as rsxml
from resync import Resource


@attr.s
class Generator(object):

    params = attr.ib()
    rsxml = attr.ib(default=None, validator=optional(instance_of(rsxml.RsXML)))

    def __init__(self, **kwargs):
        pass

    def generate(self) -> [Resource]:
        raise NotImplementedError("Generator not implemented")
