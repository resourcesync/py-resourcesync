# -*- coding: utf-8 -*-

from resourcesync.resourcesync import ResourceSync
from resourcesync.generators.eg_generator import EgGenerator
from resourcesync.parameters.parameters import ParameterUtils
import unittest
import shutil
import os


class EgGeneratorTest(unittest.TestCase):

    def tearDown(self):
        try:
            shutil.rmtree(os.path.join(ParameterUtils.get_resource_dir("~"), "test_md"))
        except:
            pass

    def test_resourcesync_with_eg_generator(self):
        eg_gen = EgGenerator()
        rs = ResourceSync(strategy=0, generator=eg_gen, metadata_dir="test_md")
        rs.execute()

    def test_resourcesync_with_eg_generator_and_config_file(self):
        eg_gen = EgGenerator()
        rs = ResourceSync(config_name="DEFAULT", generator=eg_gen, metadata_dir="test_md")
        rs.execute()


if __name__ == "__main__":
    unittest.main()