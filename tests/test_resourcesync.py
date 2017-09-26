# -*- coding: utf-8 -*-

import unittest
from hashlib import md5
from resync import Resource
from resourcesync.resourcesync import ResourceSync
from resourcesync.core.generator import Generator
from resourcesync.generators.eg_generator import EgGenerator
import shutil
import os
from resourcesync.parameters.parameters import ParameterUtils


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


eg_gen = EgGenerator()


class ResourceSyncTest(unittest.TestCase):

    def tearDown(self):
        try:
            shutil.rmtree(os.path.join(ParameterUtils.get_resource_dir("~"), "test_md"))
        except:
            pass

    def test_resourcelist(self):
        rs = TestReSync(generator=eg_gen, strategy=0,
                        metadata_dir="test_md")
        rs.execute()

    def test_newchangelist(self):
        rs = TestReSync(generator=eg_gen, strategy=1,
                        metadata_dir="test_md")
        rs.execute()

    def test_incchangelist(self):
        rs = TestReSync(generator=eg_gen, strategy=2,
                        metadata_dir="test_md")
        rs.execute()

    def test_gen_not_impl(self):
        class NoGenerator(Generator):
            def __init__(self):
                pass
        nogen = NoGenerator()
        rs = ResourceSync(generator=nogen)
        with self.assertRaises(NotImplementedError):
            rs.execute()

    def test_new_params(self):
        rs = ResourceSync(new_param="blahblah")
        assert rs.params.new_param == "blahblah"

    def test_new_params_persistence(self):
        rs = ResourceSync(new_param="blahblah")
        rs.params.save_configuration(True)

        with open(rs.params.config_file, "rb") as f:
            params = f.read()
            assert b"new_param = blahblah" in params


if __name__ == "__main__":
    unittest.main()
