# -*- coding: utf-8 -*-

"""
:samp:`Example Generator component.`
"""

from resourcesync.core.generator import Generator
from hashlib import md5
from resync import Resource


class EgGenerator(Generator):

    def __init__(self, params=None, rsxml=None):
        Generator.__init__(self, params, rsxml=rsxml)

    def generate(self):

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
