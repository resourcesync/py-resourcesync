# -*- coding: utf-8 -*-
import unittest
from hashlib import md5
from resync import Resource
from resourcesync.resourcesync import ResourceSync
from resourcesync.core.generator import Generator
from resourcesync.generators.eg_generator import EgGenerator
from resourcesync.parameters.parameters import ParameterUtils
import shutil
import os


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
            mime_type="application/xml",
            change="updated"
        )
        return [rm]

eg_gen = EgGenerator()
ch_gen = ChangeGenerator()


class ResourceSyncTest(unittest.TestCase):

    def tearDown(self):
        try:
            shutil.rmtree(os.path.join(ParameterUtils.get_resource_dir("~"), "test_md"))
        except:
            pass

    def test_change_list(self):
        rs = ResourceSync(generator=eg_gen, strategy=0, metadata_dir="test_md")
        rs.execute()
        ch_rs = ResourceSync(generator=ch_gen, strategy="new_changelist", metadata_dir="test_md")
        ch_rs.execute()


