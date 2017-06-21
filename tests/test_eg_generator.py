# -*- coding: utf-8 -*-

from resourcesync.resourcesync import ResourceSync
from resourcesync.generators.eg_generator import EgGenerator
import unittest
import logging


#LOG = logging.getLogger(__name__)
#logging.basicConfig(level=logging.DEBUG)


class EgGeneratorTest(unittest.TestCase):

    def test_resourcesync_with_eg_generator(self):
        eg_gen = EgGenerator()
        rs = ResourceSync(strategy=0, generator=eg_gen)
        rs.execute()

    def test_resourcesync_with_eg_generator_and_config_file(self):
        eg_gen = EgGenerator()
        rs = ResourceSync(config_name="DEFAULT", generator=eg_gen)
        rs.execute()

if __name__ == "__main__":
    unittest.main()