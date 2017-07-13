# -*- coding: utf-8 -*-

import unittest
from resourcesync.resourcesync import ResourceSync
from resourcesync.generators.oaipmh_generator import OAIPMHGenerator
from requests_mock import mock
from tests.test_oaipmh_generator_mock_responses import mock_responses
import logging


LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class OAIPMHGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.oaipmh_base_url         = "http://example.com/oai"
        self.oaipmh_set              = "test"
        self.oaipmh_metadataprefix   = "oai_dc"
        self.oaipmh_generator_params = {
            "oaipmh_base_url":       self.oaipmh_base_url,
            "oaipmh_set":            self.oaipmh_set,
            "oaipmh_metadataprefix": self.oaipmh_metadataprefix }

        self.getrecord_url_template       = "{}?verb=GetRecord&identifier={}&metadataPrefix={}"
        self.listidentifiers_url_template = "{}?verb=ListIdentifiers&set={}&metadataPrefix={}"
        self.http_response_headers        = { "content-type": "text/xml" }

    def test_generate(self):

        with mock() as m:

            test_num = 0

            # create two records, A and B
            getrecord_A_url     = self.getrecord_url_template.format(self.oaipmh_base_url, "A", self.oaipmh_metadataprefix)
            getrecord_B_url     = self.getrecord_url_template.format(self.oaipmh_base_url, "B", self.oaipmh_metadataprefix)
            listidentifiers_url = self.listidentifiers_url_template.format(self.oaipmh_base_url, self.oaipmh_set, self.oaipmh_metadataprefix)

            m.get(getrecord_A_url,     text=mock_responses[test_num][getrecord_A_url],     headers=self.http_response_headers)
            m.get(getrecord_B_url,     text=mock_responses[test_num][getrecord_B_url],     headers=self.http_response_headers)
            m.get(listidentifiers_url, text=mock_responses[test_num][listidentifiers_url], headers=self.http_response_headers)

            metadata = OAIPMHGenerator(params=self.oaipmh_generator_params).generate()
            LOG.debug(metadata)

            # save so we can track changes to record B
            old_metadata = metadata

            # expect two records in the metadata list
            self.assertTrue(len(metadata) == 2)
            self.assertTrue(len(list(filter(lambda x: x.uri == getrecord_A_url, metadata))) == 1)
            self.assertTrue(len(list(filter(lambda x: x.uri == getrecord_B_url, metadata))) == 1)



            test_num = 1

            # delete record A, update record B, create record C
            getrecord_A_url     = self.getrecord_url_template.format(self.oaipmh_base_url, "A", self.oaipmh_metadataprefix)
            getrecord_B_url     = self.getrecord_url_template.format(self.oaipmh_base_url, "B", self.oaipmh_metadataprefix)
            getrecord_C_url     = self.getrecord_url_template.format(self.oaipmh_base_url, "C", self.oaipmh_metadataprefix)
            listidentifiers_url = self.listidentifiers_url_template.format(self.oaipmh_base_url, self.oaipmh_set, self.oaipmh_metadataprefix)

            m.get(getrecord_A_url,     text=mock_responses[test_num][getrecord_A_url],     headers=self.http_response_headers)
            m.get(getrecord_B_url,     text=mock_responses[test_num][getrecord_B_url],     headers=self.http_response_headers)
            m.get(getrecord_C_url,     text=mock_responses[test_num][getrecord_C_url],     headers=self.http_response_headers)
            m.get(listidentifiers_url, text=mock_responses[test_num][listidentifiers_url], headers=self.http_response_headers)

            metadata = OAIPMHGenerator(params=self.oaipmh_generator_params).generate()
            LOG.debug(metadata)

            # compare md5 values of each version of record B to check for updates
            old_md5 = list(filter(lambda x: x.uri == getrecord_B_url, old_metadata))[0].md5
            new_md5 = list(filter(lambda x: x.uri == getrecord_B_url, metadata))[0].md5
            updated_record_B = old_md5 != new_md5

            # expect two records in the metadata list
            # record A was deleted, record B was updated, record C was created
            self.assertTrue(len(metadata) == 2)
            self.assertTrue(len(list(filter(lambda x: x.uri == getrecord_A_url, metadata))) == 0)
            self.assertTrue(len(list(filter(lambda x: x.uri == getrecord_B_url, metadata))) == 1 and updated_record_B)
            self.assertTrue(len(list(filter(lambda x: x.uri == getrecord_C_url, metadata))) == 1)

if __name__ == "__main__":
    unittest.main()
