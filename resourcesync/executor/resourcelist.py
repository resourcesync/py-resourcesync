# -*- coding: utf-8 -*-
"""
:samp:`Executor creating resourcelists`

"""
import os

from resync import Resource
from resync import ResourceList
from resourcesync.core.executors import Executor, SitemapData
from resourcesync.parameters.enum import Capability
from resourcesync.utils import defaults


class ResourceListExecutor(Executor):
    """
    :samp:`Executes the new resourcelist strategy`

    A ResourceListExecutor clears the metadata directory and creates new resourcelist(s) every time
    the executor runs (and is_saving_sitemaps).
    """
    def prepare_metadata_dir(self):
        if self.param.is_saving_sitemaps:
            self.clear_metadata_dir()

    def generate_rs_documents(self, resource_metadata: [Resource]) -> [SitemapData]:
        sitemap_data_iter = []
        generator = self.resourcelist_generator(resource_metadata)
        for sitemap_data, sitemap in generator():
            sitemap_data_iter.append(sitemap_data)

        return sitemap_data_iter

    def create_index(self, sitemap_data_iter: iter):
        if len(sitemap_data_iter) > 1:
            resourcelist_index = ResourceList()
            resourcelist_index.sitemapindex = True
            resourcelist_index.md_at = self.date_start_processing
            resourcelist_index.md_completed = self.date_end_processing
            index_path = self.param.abs_metadata_path("resourcelist-index.xml")
            rel_index_path = os.path.relpath(index_path, self.param.resource_dir)
            index_url = self.param.url_prefix + defaults.sanitize_url_path(rel_index_path)
            resourcelist_index.link_set(rel="up", href=self.param.capabilitylist_url())

            for sitemap_data in sitemap_data_iter:
                resourcelist_index.add(Resource(uri=sitemap_data.uri, md_at=sitemap_data.doc_start,
                                      md_completed=sitemap_data.doc_end))
                if sitemap_data.document_saved:
                    self.update_rel_index(index_url, sitemap_data.path)

            self.finish_sitemap(-1, resourcelist_index)

    def resourcelist_generator(self, resource_metadata: [Resource]) -> iter:

        def generator() -> [SitemapData, ResourceList]:
            resourcelist = None
            ordinal = self.find_ordinal(Capability.resourcelist.name)
            resource_count = 0
            doc_start = None
            resource_generator = self.resource_generator()
            for resource_count, resource in resource_generator(resource_metadata):
                # stuff resource into resourcelist
                if resourcelist is None:
                    resourcelist = ResourceList()
                    doc_start = defaults.w3c_now()
                    resourcelist.md_at = doc_start

                resourcelist.add(resource)

                # under conditions: yield the current resourcelist
                if resource_count % self.param.max_items_in_list == 0:
                    ordinal += 1
                    doc_end = defaults.w3c_now()
                    resourcelist.md_completed = doc_end
                    sitemap_data = self.finish_sitemap(ordinal, resourcelist, doc_start=doc_start, doc_end=doc_end)
                    yield sitemap_data, resourcelist
                    resourcelist = None

            # under conditions: yield the current and last resourcelist
            if resourcelist:
                ordinal += 1
                doc_end = defaults.w3c_now()
                resourcelist.md_completed = doc_end
                sitemap_data = self.finish_sitemap(ordinal, resourcelist, doc_start=doc_start, doc_end=doc_end)
                yield sitemap_data, resourcelist

        return generator
