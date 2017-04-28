# -*- coding: utf-8 -*-

import unittest
from hashlib import md5
from resync import Resource
from resourcesync.resourcesync import ResourceSync


class TestReSync(ResourceSync):
    def get_resource_list(self):
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
        rs = TestReSync(generator="EgGenerator", strategy=0)
        rs.execute()

    def test_newchangelist(self):
        rs = TestReSync(generator="EgGenerator", strategy=1)
        rs.execute()

    def test_incchangelist(self):
        rs = TestReSync(generator="EgGenerator", strategy=2)
        rs.execute()

    def test_gen_not_impl(self):
        rs = ResourceSync(generator="Generator")
        with self.assertRaises(NotImplementedError):
            rs.execute()

if __name__ == "__main__":
    unittest.main()
