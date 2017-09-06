import unittest

from urllib3_mock import Responses

from resourcesync.generators.elastic_generator import ElasticGenerator
from tests.test_elastic_generator_mock_responses import elastic_mock_responses

responses = Responses('urllib3')


class TestElasticResourceList(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.params = {"resource_set": "foo-set",
                      "strategy": 0,
                      "elastic_host": "example.com",
                      "elastic_port": 9200,
                      "elastic_index": "resync-test",
                      "elastic_resource_doc_type": "resource",
                      "elastic_change_doc_type": "change",
                      "url_prefix": "http://example.com",
                      "resource_root_dir": "tmp/dir",
                      "max_items_in_list": 2}

    @responses.activate
    def test_elastic_resourcelist(self):
        test_num = 0

        url_scan = list(elastic_mock_responses[test_num])[0]
        url_scroll = list(elastic_mock_responses[test_num])[1]
        responses.add('GET', "/resync-test/resource/_search", body=elastic_mock_responses[test_num].get(url_scan), content_type='application/json', status=200)
        responses.add('GET', "/_search/scroll", body=elastic_mock_responses[test_num].get(url_scroll), content_type='application/json', status=200)
        responses.add('DELETE', "/resync-test/change/_query", content_type='application/json', status=200)

        eg = ElasticGenerator(params=self.params)

        resourcelist = []
        for result in eg.generate():
            resourcelist.append(result)

        self.assertEqual(len(resourcelist), 2)

if __name__ == '__main__':
    unittest.main()
