#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:samp:`Executors creating changedumps`

Concrete classes:
    - :class:`NewChangeDumpExecutor`
    - :class:`IncrementalChangeDumpExecutor`

"""
import os
from abc import ABCMeta
from glob import glob
from resync import ChangeDump, ChangeList
from resync.dump import Dump, DumpError
from resync import Resource, ResourceList, ResourceDump
from resync.sitemap import Sitemap
from resourcesync.core.executors import Executor, SitemapData, ExecutorEvent
from resourcesync.parameters.enum import Capability
from resourcesync.parameters.parameters import Parameters
from resourcesync.utils import defaults
from resync.change_dump_manifest import ChangeDumpManifest
from resync.resource_dump_manifest import ResourceDumpManifest

class ChangeDumpExecutor(Executor, metaclass=ABCMeta):
    """
    :samp:`Abstract class for creating changedumps`

    """

    def __init__(self, parameters: Parameters=None):
        Executor.__init__(self, parameters)

        # next parameters will all be set in the method update_previous_state
        self.previous_resources = None
        self.date_resourcelist_completed = None
        self.date_changedump_from = None
        self.resourcelist_files = []
        self.changedump_files = []
        ##

    def generate_rs_documents(self, resource_metadata: [Resource] ) -> [SitemapData, Resource]:
        sitemap_data_iter = []
        rdumps_iter = []
        generator = self.changedump_generator(resource_metadata)

        print ('generate_rs_document')
        for sitemap_data, resource in generator():
            sitemap_data_iter.append(sitemap_data)
            rdumps_iter.append(resource)
        # self.create_index(sitemap_data_iter, rdumps_iter)
        # self.create_index(rdumps_iter)
        # self.create_index(sitemap_data_iter)

        return sitemap_data_iter, rdumps_iter

    def create_index(self, sitemap_data_iter: iter) -> SitemapData:
        changelist_index_path = self.param.abs_metadata_path("changedump-index.xml")
        changelist_index_uri = self.param.uri_from_path(changelist_index_path)
        if os.path.exists(changelist_index_path):
            os.remove(changelist_index_path)

        changelist_files = sorted(glob(self.param.abs_metadata_path("changedump_*.xml")))
        changedump_files = sorted(glob(self.param.abs_metadata_path("cd_*.zip")))
        if len(changelist_files) > 1:
            # changelist_index = ChangeDumpManifest()
            changelist_index = ChangeDump()
            changelist_index.modified=defaults.w3c_now()
            # changelist_index.sitemapindex = True
            # changelist_index.modified = self.date_resourcelist_completed
            for cl_file, cd_file in zip(changelist_files, changedump_files):
                # changelist = self.read_sitemap(cl_file, ChangeDump(md_from=changelist.md_from, md_until=changelist.md_until))
                changelist = self.read_sitemap(cl_file, ChangeDump())
                uri = self.param.uri_from_path(cd_file)
                lastmod = str(defaults.reformat_datetime(defaults.file_modification_date(cd_file)))
                md5 = defaults.md5_for_file(cd_file)
                mime_type = defaults.mime_type(cd_file)
                cd_length = os.path.getsize(cd_file)
                cd = Resource(uri=uri, length=cd_length, lastmod=lastmod, ln=[{'rel': 'contents', 'href':cl_file}])
                # changelist_index.resources.add(Resource(uri=uri, length=cd_length, md_from=changelist.md_from, 
                changelist_index.add(cd)
                

                if self.param.is_saving_sitemaps:
                    index_link = changelist.link("index")
                    if index_link is None:
                        changelist.link_set(rel="index", href=changelist_index_uri)
                        self.save_sitemap(changelist, cl_file)

            self.finish_sitemap(-1, changelist_index)

    def update_previous_state(self):
        if self.previous_resources is None:
            self.previous_resources = {}

            # search for resourcelists
            self.resourcelist_files = sorted(glob(self.param.abs_metadata_path("changedump_*.xml")))
            for rl_file_name in self.resourcelist_files:
                resourcelist = ResourceList()
                with open(rl_file_name, "r", encoding="utf-8") as rl_file:
                    sm = Sitemap()
                    sm.parse_xml(rl_file, resources=resourcelist)

                self.date_resourcelist_completed = resourcelist.md_completed
                if self.date_resourcelist_completed is None:
                    self.date_resourcelist_completed = resourcelist.md_at

                self.previous_resources.update({resource.uri: resource for resource in resourcelist.resources})

            # search for changedumps
            self.changedump_files = sorted(glob(self.param.abs_metadata_path("changedump_*.xml")))
            for cl_file_name in self.changedump_files:
                changedump = ChangeDump()
                with open(cl_file_name, "r", encoding="utf-8") as cl_file:
                    sm = Sitemap()
                    sm.parse_xml(cl_file, resources=changedump)

                for resource in changedump.resources:
                    if resource.change == "created" or resource.change == "updated":
                        self.previous_resources.update({resource.uri: resource})
                    elif resource.change == "deleted" and resource.uri in self.previous_resources:
                        del self.previous_resources[resource.uri]

    def changedump_generator(self, resource_metadata: [Resource]) -> [iter,iter]:
        # def changedump_generator(self, resource_metadata: [Resource]) -> iter:

        def generator(changedump=None) -> [SitemapData, ChangeDump]:

            resource_generator = self.resource_generator()
            self.update_previous_state()
            prev_r = self.previous_resources
            curr_r = {resource.uri: resource for count, resource in resource_generator(resource_metadata)}
            created = [r for r in curr_r.values() if r.uri not in prev_r]
            updated = [r for r in curr_r.values() if r.uri in prev_r and r.md5 != prev_r[r.uri].md5]
            deleted = [r for r in prev_r.values() if r.uri not in curr_r]
            unchang = [r for r in curr_r.values() if r.uri in prev_r and r.md5 == prev_r[r.uri].md5]

            # remove lastmod from deleted resource metadata
            for resource in deleted:
                resource.lastmod = None

            num_created = len(created)
            num_updated = len(updated)
            num_deleted = len(deleted)
            tot_changes = num_created + num_updated + num_deleted
            self.observers_inform(self, ExecutorEvent.found_changes, created=num_created, updated=num_updated,
                                  deleted=num_deleted, unchanged=len(unchang))
            all_changes = {"created": created, "updated": updated, "deleted": deleted}

            ordinal = self.find_ordinal(Capability.changedump.name)

            resource_count = 0
            if changedump:
                ordinal -= 1
                resource_count = len(changedump)
                if resource_count >= self.param.max_items_in_list:
                    changedump = None
                    ordinal += 1
                    resource_count = 0

            for kv in all_changes.items():
                for resource in kv[1]:
                    if changedump is None:
                        changedump = ChangeDump()
                        changedump.md_from = self.date_changedump_from

                    resource.change = kv[0] # type of change: created, updated or deleted
                    resource.md_datetime = self.date_start_processing
                    changedump.add(resource)

                    resource_count += 1

                    # under conditions: yield the current changedump
                    if resource_count % self.param.max_items_in_list == 0:
                        ordinal += 1
                        # sitemap_data = self.finish_sitemap(ordinal, changedump)
                        d = Dump(resources = changedump)
                        # zipf = os.path.join('/tmp', "cd_" + str(ordinal) + ".zip")
                        zipf = self.param.abs_metadata_path("cd_" + str(ordinal) + ".zip")
                        print (str(zipf))
                        d.write_zip(resources=changedump, dumpfile=zipf)
                        doc_end = defaults.w3c_now()

                        sitemap_data = self.finish_sitemap(ordinal, changedump, doc_start=self.date_start_processing, doc_end=doc_end)
                        # dumpResource = ChangeDump(Resource(uri=str(zipf)))
                        dumpResource = ChangeDump(uri=str(zipf))
                        # yield sitemap_data, changedump
                        yield sitemap_data, dumpResource
                        # yield sitemap_data, zipf
                        # yield zipf
                        changedump = None


            # under conditions: yield the current and last changedump
            if changedump and tot_changes > 0:
                ordinal += 1
                doc_end = defaults.w3c_now()
                changedump.md_completed = doc_end
                d = Dump()
                zipf = self.param.abs_metadata_path("cd_" + str(ordinal) + ".zip")
                print (str(zipf))
                sitemap_data = self.finish_sitemap(ordinal, changedump, doc_start=self.date_start_processing, doc_end=doc_end)
                # dumpResource = ChangeDump(Resource(uri=str(zipf)))
                dumpResource = ChangeDump(uri=str(zipf))
                # dumpResource = ChangeDump(uri=str(zipf))
                # yield sitemap_data, changedump
                yield sitemap_data, dumpResource
                # yield sitemap_data, zipf
                # yield zipf
                d.write_zip(resources=changedump, dumpfile=zipf)


        return generator


class NewChangeDumpExecutor(ChangeDumpExecutor):
    """
    :samp:`Implements the new changedump strategy`

    A :class:`NewChangeDumpExecutor` creates new changedumps every time the executor runs (and is_saving_sitemaps).
    If there are previous changedumps that are not closed (md:until is not set) this executor will close
    those previous changedumps by setting their md:until value to now (start_of_processing)
    """
    def generate_rs_documents(self, resource_metadata: [Resource]):
        self.update_previous_state()
        if len(self.changedump_files) == 0:
            self.date_changedump_from = self.date_resourcelist_completed
        else:
            self.date_changedump_from = self.date_start_processing

        sitemap_data_iter = []
        generator = self.changedump_generator(resource_metadata)
        print ('NewChangeDumpExecutor')
        for sitemap_data, changedump in generator():
            sitemap_data_iter.append(sitemap_data)

        return sitemap_data_iter

    def post_process_documents(self, sitemap_data_iter: iter):
        # change md:until value of older changedumps - if we created new changedumps.
        # self.changedump_files was globed before new documents were generated (self.update_previous_state).
        if len(sitemap_data_iter) > 0 and self.param.is_saving_sitemaps:
            for filename in self.changedump_files:
                changedump = self.read_sitemap(filename, ChangeDump())
                if changedump.md_until is None:
                    changedump.md_until = self.date_start_processing
                    self.save_sitemap(changedump, filename)


class IncrementalChangeDumpExecutor(ChangeDumpExecutor):
    """
    :samp:`Implements the incremental changedump strategy`

    An :class:`IncrementalChangeDumpExecutor` adds changes to an already existing changedump every time
    the executor runs
    (and is_saving_sitemaps).
    """
    def generate_rs_documents(self, resource_metadata: iter):
        self.update_previous_state()
        self.date_changedump_from = self.date_resourcelist_completed
        changedump = None
        if len(self.changedump_files) > 0:
            changedump = self.read_sitemap(self.changedump_files[-1], ChangeDump())

        sitemap_data_iter = []
        generator = self.changedump_generator(resource_metadata)

        for sitemap_data, changedump in generator(changedump=changedump):
            sitemap_data_iter.append(sitemap_data)

