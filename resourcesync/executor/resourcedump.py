# -*- coding: utf-8 -*-
"""
:samp:`Executor creating resourcedumps`

"""
import os

from resync.dump import Dump, DumpError
from resourcesync.core.executors import Executor, SitemapData
from resourcesync.parameters.enum import Capability
from resourcesync.utils import defaults
from resync.resource_list import ResourceList
from resync.resource import Resource
from resync.resource_dump_manifest import ResourceDumpManifest
from resync import ResourceDump


class ResourceDumpExecutor(Executor):
    """
    :samp:`Executes the new resourcedump strategy`

    A ResourceDumpExecutor clears the metadata directory and creates new resourcedump(s) every time
    the executor runs (and is_saving_sitemaps).
    """
    def prepare_metadata_dir(self):
        if self.param.is_saving_sitemaps:
            self.clear_metadata_dir()

    def generate_rs_documents(self, resource_metadata: [Resource] ) -> [Resource]:
        sitemap_data_iter = []
        rdumps_iter = []
        generator = self.resourcedump_generator(resource_metadata)
        for resource in generator():
            rdumps_iter.append(resource)
        self.create_index(rdumps_iter)
        return rdumps_iter

    def create_index(self, rdumps_iter: iter):
        if len(rdumps_iter) > 1:

            # resourcelist_index = ResourceList()
            resourcelist_index = ResourceDump()
            resourcelist_index.sitemapindex = True
            resourcelist_index.md_at = self.date_start_processing
            resourcelist_index.md_completed = self.date_end_processing
            index_path = self.param.abs_metadata_path("resourcedump-index.xml")
            rel_index_path = os.path.relpath(index_path, self.param.resource_dir)
            index_url = self.param.url_prefix + defaults.sanitize_url_path(rel_index_path)
            resourcelist_index.link_set(rel="up", href=self.param.capabilitylist_url())

            for resource in rdumps_iter:
                print(resource.uri)
                resourcelist_index.add(Resource(uri=resource.uri))

            self.finish_sitemap(-1, resourcelist_index)

    def resourcedump_generator(self, resource_metadata: [Resource]) -> [iter,iter]:

        # def generator() -> [SitemapData, ResourceDumpManifest]:
        def generator() -> [SitemapData, Resource]:
            resourcedump = None
            ordinal = self.find_ordinal(Capability.resourcedump.name)
            resource_count = 0
            doc_start = None
            resource_generator = self.resource_generator()
            for resource_count, resource in resource_generator(resource_metadata):
                # stuff resource into resourcedump
                if resourcedump is None:
                    # resourcedump = ResourceDumpManifest()
                    resourcedump = ResourceDump()
                    doc_start = defaults.w3c_now()
                    resourcedump.md_at = doc_start

                resourcedump.add(resource)

                # under conditions: yield the current resourcedump
                if resource_count % self.param.max_items_in_list == 0:
                    ordinal += 1
                    doc_end = defaults.w3c_now()
                    resourcedump.md_completed = doc_end
                    d = Dump(resources = resourcedump)
                    zipf = self.param.abs_metadata_path("rd_" + str(ordinal) + ".zip")

                    print (str(zipf))
                    d.write_zip(resources=resourcedump, dumpfile=zipf)
                    dumpResource = Resource(uri=str(zipf))
                    yield dumpResource
                    resourcedump = None


            # under conditions: yield the current and last resourcedump
            if resourcedump:
                ordinal += 1
                doc_end = defaults.w3c_now()
                resourcedump.md_completed = doc_end
                d = Dump()
                zipf = self.param.abs_metadata_path("rd_" + str(ordinal) + ".zip")
                print (str(zipf))
                dumpResource = Resource(uri=str(zipf))
                yield dumpResource
                d.write_zip(resources=resourcedump, dumpfile=zipf)
       
        return generator
