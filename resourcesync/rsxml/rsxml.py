# -*- coding: utf-8 -*-

"""
:samp:`Converts ResourceSync sitemaps from xml to classes and vise-versa.

#TODO
"""

from resync.sitemap import Sitemap


class RsXML(object):

    def __init__(self):
        self.res_container = None

    def __len__(self):
        if self.res_container:
            return len(self.res_container.resources)

    def parse_xml(self, fh=None, etree=None, resources=None,
                  capability=None, sitemapindex=None):

        """Parse XML Sitemap and add to resources object.

        Reads from fh or etree and adds resources to a resorces object
        (which must support the add method). Returns the resources object.

        Also sets self.resources_created to be the number of resources created.
        We adopt a very lax approach here. The parsing is properly namespace
        aware but we search just for the elements wanted and leave everything
        else alone.

        This method will read either sitemap or sitemapindex documents. Behavior
        depends on the sitemapindex parameter:
        - None - will read either
        - False - SitemapIndexError exception if sitemapindex detected
        - True - SitemapIndexError exception if sitemap detected

        Will set self.parsed_index based on whether a sitemap or sitemapindex
        document was read:
        - False - sitemap
        - True - sitemapindex
        """

        sitemap = Sitemap()
        self.res_container = sitemap.parse_xml(fh=fh, etree=etree, resources=resources,
                                               capability=capability, sitemapindex=sitemapindex)
        return self.res_container

    def convert_to_xml(self, resources, sitemap_index=False, fh=None):
        """Write or return XML for a set of resources in sitemap format.

        Arguments:
        - resources - either an iterable or iterator of Resource objects;
                      if there an md attribute this will go to <rs:md>
                      if there an ln attribute this will go to <rs:ln>
        - sitemapindex - set True to write sitemapindex instead of sitemap
        - fh - write to filehandle fh instead of returning string
        """
        sitemap = Sitemap()
        self.res_container = resources
        if len(self.res_container) == 0:
            return
        return sitemap.resources_as_xml(self.res_container, sitemapindex=sitemap_index, fh=fh)
