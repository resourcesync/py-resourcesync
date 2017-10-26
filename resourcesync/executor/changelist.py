#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:samp:`Executors creating changelists`

Concrete classes:
    - :class:`NewChangeListExecutor`
    - :class:`IncrementalChangeListExecutor`

"""
import os
from abc import ABCMeta
from glob import glob
from resync import ChangeList
from resync import Resource
from resync import ResourceList
from resync.sitemap import Sitemap

from resourcesync.core.executors import Executor, SitemapData, ExecutorEvent
from resourcesync.parameters.enum import Capability
from resourcesync.parameters.parameters import Parameters
from resourcesync.rsxml.rsxml import RsXML


class ChangeListExecutor(Executor, metaclass=ABCMeta):
    """
    :samp:`Abstract class for creating changelists`

    """
    def generate_rs_documents(self, resource_metadata: [Resource]) -> [SitemapData]:
        pass

    def __init__(self, parameters: Parameters=None):
        Executor.__init__(self, parameters)

        # next parameters will all be set in the method update_previous_state
        self.previous_resources = None
        self.date_resourcelist_completed = None
        self.date_changelist_from = None
        self.resourcelist_files = []
        self.changelist_files = []
        ##

    def create_index(self, sitemap_data_iter: iter) -> SitemapData:
        changelist_index_path = self.param.abs_metadata_path("changelist-index.xml")
        changelist_index_uri = self.param.uri_from_path(changelist_index_path)
        if os.path.exists(changelist_index_path):
            os.remove(changelist_index_path)

        changelist_files = sorted(glob(self.param.abs_metadata_path("changelist_*.xml")))
        if len(changelist_files) > 1:
            changelist_index = ChangeList()
            changelist_index.sitemapindex = True
            changelist_index.md_from = self.date_resourcelist_completed
            for cl_file in changelist_files:
                changelist = self.read_sitemap(cl_file, ChangeList())
                uri = self.param.uri_from_path(cl_file)
                changelist_index.resources.append(Resource(uri=uri, md_from=changelist.md_from,
                                                           md_until=changelist.md_until))

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
            self.resourcelist_files = sorted(glob(self.param.abs_metadata_path("resourcelist_*.xml")))
            for rl_file_name in self.resourcelist_files:
                resourcelist = ResourceList()
                with open(rl_file_name, "r", encoding="utf-8") as rl_file:
                    sm = Sitemap()
                    sm.parse_xml(rl_file, resources=resourcelist)

                self.date_resourcelist_completed = resourcelist.md_completed
                if self.date_resourcelist_completed is None:
                    self.date_resourcelist_completed = resourcelist.md_at

            # search for changelists
            self.changelist_files = sorted(glob(self.param.abs_metadata_path("changelist_*.xml")))

    def changelist_generator(self, resource_metadata: [Resource]) -> iter:

        def generator(changelist=None) -> [SitemapData, ChangeList]:
            change_generator = self.resource_generator()
            changes = [change for count, change in change_generator(resource_metadata)]
            created = [c for c in changes if c.change == 'created']
            updated = [c for c in changes if c.change == 'updated']
            deleted = [c for c in changes if c.change == 'deleted']

            num_created = len(created)
            num_updated = len(updated)
            num_deleted = len(deleted)
            tot_changes = num_created + num_updated + num_deleted
            self.observers_inform(self, ExecutorEvent.found_changes, created=num_created, updated=num_updated,
                                  deleted=num_deleted)

            ordinal = self.find_ordinal(Capability.changelist.name)

            resource_count = 0
            if changelist:
                ordinal -= 1
                resource_count = len(changelist)
                if resource_count >= self.param.max_items_in_list:
                    changelist = None
                    ordinal += 1
                    resource_count = 0

            for change in changes:
                if changelist is None:
                    changelist = ChangeList()
                    changelist.md_from = self.date_changelist_from

                changelist.add(change)
                resource_count += 1

                # under conditions: yield the current changelist
                if resource_count % self.param.max_items_in_list == 0:
                    ordinal += 1
                    sitemap_data = self.finish_sitemap(ordinal, changelist)
                    yield sitemap_data, changelist
                    changelist = None

            # under conditions: yield the current and last changelist
            if changelist and tot_changes > 0:
                ordinal += 1
                sitemap_data = self.finish_sitemap(ordinal, changelist)
                yield sitemap_data, changelist

        return generator


class NewChangeListExecutor(ChangeListExecutor):
    """
    :samp:`Implements the new changelist strategy`

    A :class:`NewChangeListExecutor` creates new changelists every time the executor runs (and is_saving_sitemaps).
    If there are previous changelists that are not closed (md:until is not set) this executor will close
    those previous changelists by setting their md:until value to now (start_of_processing)
    """
    def generate_rs_documents(self, resource_metadata: [Resource]):
        self.update_previous_state()
        if len(self.changelist_files) == 0:
            self.date_changelist_from = self.date_resourcelist_completed
        else:
            self.date_changelist_from = self.date_start_processing

        sitemap_data_iter = []
        generator = self.changelist_generator(resource_metadata)
        for sitemap_data, changelist in generator():
            sitemap_data_iter.append(sitemap_data)

        return sitemap_data_iter

    def post_process_documents(self, sitemap_data_iter: iter):
        # change md:until value of older changelists - if we created new changelists.
        # self.changelist_files was globed before new documents were generated (self.update_previous_state).
        if len(sitemap_data_iter) > 0 and self.param.is_saving_sitemaps:
            for filename in self.changelist_files:
                changelist = self.read_sitemap(filename, ChangeList())
                if changelist.md_until is None:
                    changelist.md_until = self.date_start_processing
                    self.save_sitemap(changelist, filename)


class IncrementalChangeListExecutor(ChangeListExecutor):
    """
    :samp:`Implements the incremental changelist strategy`

    An :class:`IncrementalChangeListExecutor` adds changes to an already existing changelist every time
    the executor runs
    (and is_saving_sitemaps).
    """
    def generate_rs_documents(self, resource_metadata: iter):
        self.update_previous_state()
        self.date_changelist_from = self.date_resourcelist_completed
        changelist = None
        if len(self.changelist_files) > 0:
            changelist = self.read_sitemap(self.changelist_files[-1], ChangeList())

        sitemap_data_iter = []
        generator = self.changelist_generator(resource_metadata)

        for sitemap_data, changelist in generator(changelist=changelist):
            sitemap_data_iter.append(sitemap_data)

        return sitemap_data_iter
