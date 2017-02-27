# -*- coding: utf-8 -*-

from .context import resource_metadata
import unittest
from datetime import datetime
from hashlib import md5


class ResourceMetadataTest(unittest.TestCase):

    def test_constructor(self):

        url = "http://www.resourcesync.org"
        m = md5()
        m.update(url.encode("utf8"))

        self.assertIsInstance(resource_metadata.ResourceMetadata(
            loc=url,
            lastmod=datetime.now(),
            hash=m.hexdigest(),
            length=20,
            typ="application/xml"
        ), resource_metadata.ResourceMetadata)

        # making sure constructor accepts mandatory parameters
        with self.assertRaises(TypeError):
            resource_metadata.ResourceMetadata()

        # lastmod shd be of type datetime
        with self.assertRaises(TypeError):
            resource_metadata.ResourceMetadata(
                loc=url,
                lastmod="2016-20-01",
                hash=m.hexdigest(),
                length=20,
                typ="application/xml"
            )

if __name__ == "__main__":
    unittest.main()
