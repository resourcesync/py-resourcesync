# -*- coding: utf-8 -*-

from resourcesync.rsxml.rsxml import RsXML
import unittest
from io import StringIO
from resourcesync.generators.eg_generator import EgGenerator
from resourcesync.parameters.parameters import Parameters

SAMPLE_XML = """<?xml version='1.0' encoding='UTF-8'?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:rs="http://www.openarchives.org/rs/terms/">
<rs:ln href="http://www.example.com/metadata/capabilitylist.xml" rel="up" />
<rs:md at="2017-03-30T17:32:10Z" capability="resourcelist" completed="2017-03-30T17:32:10Z" />
<url><loc>http://www.resourcesync.org</loc><lastmod>2016-10-01T00:00:00Z</lastmod><rs:md hash="md5:cc9895a21e335bbe66d61f2b62ce3a8e" length="20" type="application/xml" /></url>
</urlset>"""


class RsXMLTest(unittest.TestCase):

    def test_parse_xml(self):
        sample = StringIO(SAMPLE_XML)
        rsxml = RsXML()
        rs_cont = rsxml.parse_xml(fh=sample)
        assert len(rs_cont.resources) > 0

    def test_convert_to_xml(self):
        eg = EgGenerator(Parameters())
        rsxml = RsXML()
        xml = rsxml.convert_to_xml(eg.generate())
        assert xml is not None
