# -*- coding: utf-8 -*-
import unittest
from hashlib import md5
from resync import Resource
from resourcesync.resourcesync import ResourceSync
from resourcesync.core.generator import Generator
from resourcesync.generators.eg_generator import EgGenerator
import logging


#logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)


class ChangeGenerator(Generator):

    def __init__(self, params=None, rsxml=None):
        Generator.__init__(self, params, rsxml=rsxml)

    def generate(self):

        url = "http://www.resourcesync.org"
        m = md5()
        body = url + "new changes"
        m.update(body.encode("utf8"))
        rm = Resource(
            uri=url,
            lastmod="2017-06-14",
            md5=m.hexdigest(),
            length=len(body),
            mime_type="application/xml"
        )
        return [rm]

eg_gen = EgGenerator()
ch_gen = ChangeGenerator()


class ResourceSyncTest(unittest.TestCase):

    def test_change_list(self):
        rs = ResourceSync(generator=eg_gen, strategy=0)
        rs.execute()
        ch_rs = ResourceSync(generator=ch_gen, strategy="new_changelist")
        ch_rs.execute()


