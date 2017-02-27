# -*- coding: utf-8 -*-

"""
:samp:`Resource Metadata data structure. Alternate to :class:`resync.Resource`.

Not being used currently, will be removed.
"""


import attr
from attr.validators import instance_of, optional
from datetime import datetime


@attr.s
class ResourceMetadata(object):

    loc = attr.ib(validator=instance_of(str))
    lastmod = attr.ib(validator=instance_of(datetime))
    hash = attr.ib(validator=instance_of(str))
    length = attr.ib(validator=instance_of(int))
    typ = attr.ib()
    change = attr.ib(default=None, validator=optional(instance_of(str)))
    datetime = attr.ib(default=None, validator=optional(instance_of(datetime)))

