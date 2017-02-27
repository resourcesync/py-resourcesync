# -*- coding: utf-8 -*-

from .context import ResourceSync
import unittest
from hashlib import md5
from resync import Resource
from resourcesync.core.generator import Generator


class TestReSync(ResourceSync):
    def get_resource_metadata(self):
        url = "http://www.resourcesync.org"
        m = md5()
        m.update(url.encode("utf8"))

        rm = Resource(
            uri=url,
            lastmod="2016-10-01",
            md5=m.hexdigest(),
            length=20,
            mime_type="application/xml"
        )
        return [rm]


class ResourceSyncTest(unittest.TestCase):

    def test_resourcelist(self):
        rs = TestReSync()
        rs.params.strategy = 0
        rs.params.generator = "resourcesync.generators.eg_generator.EgGenerator"
        rs.execute()

    def test_newchangelist(self):
        rs = TestReSync()
        rs.params.strategy = 1
        rs.params.generator = "resourcesync.generators.eg_generator.EgGenerator"
        rs.execute()

    def test_incchangelist(self):
        rs = TestReSync()
        rs.params.strategy = 2
        rs.params.generator = "resourcesync.generators.eg_generator.EgGenerator"
        rs.execute()

    def test_gen_not_impl(self):
        rs = ResourceSync()
        rs.params.generator = Generator
        with self.assertRaises(NotImplementedError):
            rs.execute()

if __name__ == "__main__":
    unittest.main()
