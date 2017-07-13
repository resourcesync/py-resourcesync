# -*- coding: utf-8 -*-

"""
:samp:`An OAI-PMH Generator.`
"""

from resourcesync.core.generator import Generator
from hashlib import md5
from resync import Resource
from sickle import Sickle
from requests import get
from bs4 import BeautifulSoup


class OAIPMHGenerator(Generator):
    """Generator class for using ResourceSync with OAI-PMH records.

    This generator expects a dictionary supplied via the `params` kwarg with
    the following keys set:

    oaipmh_base_url         the base URL for OAI-PMH requests, to which query
        parameters are appended to form the full request URL

    oaipmh_set              the set argument, as defined in
        https://www.openarchives.org/OAI/openarchivesprotocol.html#Set

    oaipmh_metadataprefix   the metadata prefix argument, as defined in
        https://www.openarchives.org/OAI/openarchivesprotocol.html#MetadataNamespaces
    """
    def __init__(self, params=None, rsxml=None):

        Generator.__init__(self, params, rsxml=rsxml)

    def generate(self):
        """Returns a list of ResourceSync resources that each represent one
        full OAI-PMH record (i.e., the result of a GetRecord request).
        """

        provider = Sickle(self.params['oaipmh_base_url'])
        headers  = provider.ListIdentifiers(ignore_deleted=True,
            set=self.params['oaipmh_set'],
            metadataPrefix=self.params['oaipmh_metadataprefix'])

        return list(map(self.oaipmh_header_to_resourcesync_resource, headers))

    def oaipmh_header_to_resourcesync_resource(self, header):
        """Maps an OAI-PMH record identifier to a ResourceSync Resource.

        header              an instance of `sickle.models.Header`
            https://sickle.readthedocs.io/en/latest/api.html#sickle.models.Header
        """

        soup       = BeautifulSoup(header.raw.encode('utf-8'), 'xml')
        lastmod    = soup.header.datestamp.text
        identifier = soup.identifier.text

        uri = '{}?verb=GetRecord&identifier={}&metadataPrefix={}'.format(
            self.params['oaipmh_base_url'],
            identifier,
            self.params['oaipmh_metadataprefix'])

        # do a GET request for each record to retrieve the 'content-length'
        r      = get(uri)
        length = len(r.content)

        # compute md5 of the GetRecord element (OAI-PMH responses include
        # responseDate tags, so the md5 of the entire response is different for
        # subsequent requests for the same record)
        m       = md5()
        element = str(BeautifulSoup(r.content, 'xml').GetRecord).encode('utf-8')
        m.update(element)

        return Resource(
            uri=uri,
            lastmod=lastmod,
            md5=m.hexdigest(),
            length=length,
            mime_type="text/xml")
