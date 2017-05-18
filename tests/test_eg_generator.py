# -*- coding: utf-8 -*-

from resourcesync.resourcesync import ResourceSync
import unittest
import logging


#LOG = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)


class EgGeneratorTest(unittest.TestCase):

    def test_resourcesync_with_eg_generator(self):
        rs = ResourceSync(strategy=0, generator="EgGenerator")
        rs.execute()

    def test_resourcesync_with_eg_generator_and_config_file(self):
        rs = ResourceSync(config_name="DEFAULT")
        rs.execute()

if __name__ == "__main__":
    unittest.main()