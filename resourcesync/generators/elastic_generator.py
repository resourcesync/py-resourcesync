# -*- coding: utf-8 -*-

"""
:samp:`Elasticsearch Generator component.`
"""
import logging

from resourcesync.core.generator import Generator
from resync import Resource

from resourcesync.generators.elastic.elastic_parameters import ElasticParameters
from resourcesync.generators.elastic.elastic_query_manager import ElasticQueryManager
from resourcesync.generators.elastic.model.change_doc import ChangeDoc
from resourcesync.generators.elastic.model.resource_doc import ResourceDoc
from resourcesync.parameters.enum import Strategy

MAX_RESULT_WINDOW = 10000

logger = logging.getLogger(__name__)


class ElasticGenerator(Generator):

    def __init__(self, params, rsxml=None):
        Generator.__init__(self, params, rsxml=rsxml)
        self.elastic_params = ElasticParameters(**params)
        self.query_manager = ElasticQueryManager(self.elastic_params.elastic_host, self.elastic_params.elastic_port)

    def generate(self) -> [Resource]:

            elastic_page_generator = self.elastic_page_generator()
            erased_changes = False
            for e_page in elastic_page_generator():
                if not erased_changes:
                    # this will happen at the first scroll
                    self.erase_changes()
                    logger.info("Erasing changes")
                    erased_changes = True
                for e_hit in e_page:
                    e_source = e_hit['_source']

                    if self.elastic_params.strategy == Strategy.resourcelist.value:
                        e_doc = ResourceDoc.as_resource_doc(e_source)
                    else:
                        e_doc = ChangeDoc.as_change_doc(e_source)

                    uri = e_doc.location.uri_from_path(param_url_prefix=self.elastic_params.url_prefix,
                                                       param_resource_root_dir=self.elastic_params.resource_root_dir)
                    if self.elastic_params.strategy == Strategy.resourcelist.value:
                        ln = []
                        if e_doc.ln:
                            for link in e_doc.ln:
                                link_uri = link.href.uri_from_path(param_url_prefix=self.elastic_params.url_prefix,
                                                                   param_resource_root_dir=self.elastic_params.resource_root_dir)
                                ln.append({'href': link_uri, 'rel': link.rel, 'mime': link.mime})

                        resource = Resource(uri=uri, length=e_doc.length,
                                            lastmod=e_doc.lastmod,
                                            md5=e_doc.md5,
                                            mime_type=e_doc.mime,
                                            ln=ln)
                    else:
                        resource = Resource(uri=uri,
                                            lastmod=e_doc.lastmod,
                                            change=e_doc.change)
                    yield resource

    def elastic_page_generator(self) -> iter:

        def generator() -> iter:
            if self.elastic_params.strategy == Strategy.resourcelist.value:
                doc_type = self.elastic_params.elastic_resource_doc_type
                query = self.resource_query()
            else:
                doc_type = self.elastic_params.elastic_change_doc_type
                query = self.change_query()

            return self.query_manager.scan_and_scroll(index=self.elastic_params.elastic_index,
                                                      doc_type=doc_type,
                                                      query=query,
                                                      max_items_in_list=self.elastic_params.max_items_in_list,
                                                      max_result_window=MAX_RESULT_WINDOW)

        return generator

    def erase_changes(self):
        self.query_manager.delete_all_index_set_type_docs(index=self.elastic_params.elastic_index,
                                                          doc_type=self.elastic_params.elastic_change_doc_type,
                                                          resource_set=self.elastic_params.resource_set)

    def resource_query(self):
        return {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "term": {"resource_set": self.elastic_params.resource_set}
                            }
                        ]
                    }
                }
            }

    def change_query(self):
        return {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "term": {"resource_set": self.elastic_params.resource_set}
                            }
                        ]
                    }
                },
                "sort": [
                    {
                        "_timestamp": {
                            "order": "asc"
                        }
                    }
                ]
            }
