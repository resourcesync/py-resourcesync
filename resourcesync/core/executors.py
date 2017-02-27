# -*- coding: utf-8 -*-

import logging
import os
import re
from abc import ABCMeta, abstractmethod
from enum import Enum
from glob import glob

from resync import CapabilityList
from resync import Resource
from resync import SourceDescription
from resync.list_base_with_index import ListBaseWithIndex
from resync.sitemap import Sitemap

from resourcesync.parameters.parameters import Parameters
from resourcesync.utils.observe import Observable, ObserverInterruptException
from resourcesync.utils import defaults
from resourcesync.parameters.enum import Capability

LOG = logging.getLogger(__name__)
WELL_KNOWN_PATH = os.path.join(".well-known", "resourcesync")


class ExecutorEvent(Enum):
    """
    :samp:`Events fired by {Executors}`

    There are information events (``inform``) and confirmation events (``confirm``). If an
    :class:`~rspub.util.observe.Observer` overrides the method :func:`~rspub.util.observe.Observer.confirm`
    and returns ``False`` on a ``confirm`` event,
    an :class:`~rspub.util.observe.ObserverInterruptException` is raised.

    All events are broadcast in the format::

        [inform][confirm](source, event, **kwargs)

    where ``source`` is the calling instance, ``event`` is the relevant event and ``**kwargs`` hold relevant
    information about the event.

    .. note:: All events are numbered, although numbers may not show in generated documentation.
    """
    # # information events
    # common low-level events
    rejected_file = 1
    """
    ``1`` ``inform`` :samp:`File rejected by resource gate`
    """
    start_file_search = 2
    """
    ``2`` ``inform`` :samp:`File search was started`
    """
    created_resource = 3
    """
    ``3`` ``inform`` :samp:`The metadata for a resource was created`
    """
    # common mid-level events
    completed_document = 10
    """
    ``10`` ``inform`` :samp:`A sitemap document was completed`
    """
    # common high-level events
    found_changes = 20
    """
    ``20`` ``inform`` :samp:`Resources that changed were found`
    """
    execution_start = 30
    """
    ``30`` ``inform`` :samp:`Execution of resource synchronization started`
    """
    execution_end = 31
    """
    ``31`` ``inform`` :samp:`Execution of resource synchronization did end`
    """
    # # confirmation events
    clear_metadata_directory = 100
    """
    ``100`` ``confirm`` :samp:`Files in metadata directory will be erased`
    """


class SitemapData(object):
    """
    :samp:`Holds metadata about sitemaps`

    """
    def __init__(self, resource_count=0, ordinal=0, uri=None, path=None, capability_name=None,
                 document_saved=False):
        """
        :samp:`Initialization`

        :param int resource_count: the amount of records in the sitemap
        :param int ordinal: the ordinal number as reflected in the sitemap filename and url
        :param str uri: the url of the sitemap
        :param str path: the local path of the sitemap
        :param str capability_name: the capability of the sitemap
        :param bool document_saved: True if the sitemap was saved to disk, False otherwise
        """
        self.resource_count = resource_count
        self.ordinal = ordinal
        self.uri = uri
        self.path = path
        self.capability_name = capability_name
        self.document_saved = document_saved
        self.doc_start = None
        self.doc_end = defaults.w3c_now()

    def __str__(self):
        return "%s, resource_count: %d, ordinal: %d, saved: %s\n\t  uri: %s\n\t path: %s" \
               % (self.capability_name, self.resource_count, self.ordinal, str(self.document_saved),
                  self.uri, self.path)


class Executor(Observable, metaclass=ABCMeta):
    """
    :samp:`Abstract base class for ResourceSync execution`

    There are 6 ``build steps`` that concrete subclasses may override (or 7 if they want to completely take over
    the execution). Two steps are mandatory for subclasses to implement: :func:`generate_rs_documents`
    and :func:`create_index`. Steps :func:`create_capabilitylist` and :func:`update_resource_sync` are not abstract -
    they can safely be done by this :class:`Executor`.
    """
    def __init__(self, parameters: Parameters=None):
        """
        :samp:`Initialization`

        If no :class:`~rspub.core.rs_paras.RsParameters` were given will construct
        new :class:`~rspub.core.rs_paras.RsParameters` from
        configuration found under :func:`~rspub.core.config.Configurations.current_configuration_name`.

        :param parameters: :class:`~rspub.core.rs_paras.RsParameters` for execution
        """

        Observable.__init__(self)
        self.param = parameters if parameters else Parameters()
        self.passes_resource_gate = None
        self.date_start_processing = None
        self.date_end_processing = None


    #def resource_gate(self):
    #    """
    #    :samp:`Construct or return the resource gate`
    #
    #    :return: resource gate
    #    """
    #    if self.passes_resource_gate is None:
    #        default_builder = ResourceGateBuilder(resource_dir=self.para.resource_dir,
    #                                              metadata_dir=self.para.abs_metadata_dir(),
    #                                              plugin_dir=self.para.plugin_dir)
    #        gate_builder = PluggedInGateBuilder(CLASS_NAME_RESOURCE_GATE_BUILDER, default_builder, self.para.plugin_dir)
    #        self.passes_resource_gate = gate_builder.build_gate()
    #    return self.passes_resource_gate

    def execute(self, resource_metadata: [Resource]):
        """
        ``build step 0`` :samp:`Publish ResourceSync documents`

        Publish ResourceSync documents under conditions of
        current :class:`~resourcesync.parameters.Parameters`.

        :param resource_metadata: iter of resource metadata `~resourcesync.core.resource_metadata.ResourceMetadata`
         instances
        """
        self.date_start_processing = defaults.w3c_now()
        self.observers_inform(self, ExecutorEvent.execution_start, date_start_processing=self.date_start_processing)
        if not os.path.exists(self.param.abs_metadata_dir()):
            os.makedirs(self.param.abs_metadata_dir())

        self.prepare_metadata_dir()
        sitemap_data_iter = self.generate_rs_documents(resource_metadata)
        self.post_process_documents(sitemap_data_iter)
        self.date_end_processing = defaults.w3c_now()
        self.create_index(sitemap_data_iter)

        capabilitylist_data = self.create_capabilitylist()
        self.update_resource_sync(capabilitylist_data)

        self.observers_inform(self, ExecutorEvent.execution_end, date_end_processing = self.date_end_processing,
                              new_sitemaps=sitemap_data_iter)

    # # Execution steps - start
    def prepare_metadata_dir(self):
        """
        ``build step 1`` :samp:`Does nothing`

        Subclasses that want to prepare metadata directory before generating new documents may override.
        """
        pass

    @abstractmethod
    def generate_rs_documents(self, resource_metadata: [Resource]) -> [SitemapData]:
        """
        ``build step 2`` :samp:`Raises {NotImplementedError}`

        Subclasses must walk resources found in ``resource_metadata`` and, if appropriate, generate sitemaps
        and produce sitemap data.

        :param resource_metadata: list of `~resourcesync.core.resource_metadata.ResourceMetadata` instances
        :return: list of :class:`SitemapData` of generated sitemaps
        """
        raise NotImplementedError

    def post_process_documents(self, sitemap_data_iter: iter):
        """
        ``build step 3`` :samp:`Does nothing`

        Subclasses that want to post proces the documents in metadata directory may override.

        :param sitemap_data_iter: iter over :class:`SitemapData` of sitemaps generated in build step 2
        """
        pass

    @abstractmethod
    def create_index(self, sitemap_data_iter: iter):
        """
        ``build step 4`` :samp:`Raises {NotImplementedError}`

        Subclasses must create sitemap indexes if appropriate.

        :param sitemap_data_iter: iter over :class:`SitemapData` of sitemaps generated in build step 2
        """
        raise NotImplementedError

    def create_capabilitylist(self) -> SitemapData:
        """
        ``build step 5`` :samp:`Create a new capabilitylist over sitemaps found in metadata directory`

        :return: :class:`SitemapData` over the newly created capabilitylist
        """
        capabilitylist_path = self.param.abs_metadata_path("capabilitylist.xml")
        if os.path.exists(capabilitylist_path) and self.param.is_saving_sitemaps:
            os.remove(capabilitylist_path)

        doc_types = ["resourcelist", "changelist", "resourcedump", "changedump"]
        capabilitylist = CapabilityList()
        for doc_type in doc_types:
            index_path = self.param.abs_metadata_path(doc_type + "-index.xml")
            if os.path.exists(index_path):
                capabilitylist.add(Resource(uri=self.param.uri_from_path(index_path), capability=doc_type))
            else:
                doc_list_files = sorted(glob(self.param.abs_metadata_path(doc_type + "_*.xml")))
                for doc_list in doc_list_files:
                    capabilitylist.add(Resource(uri=self.param.uri_from_path(doc_list), capability=doc_type))

        return self.finish_sitemap(-1, capabilitylist)

    def update_resource_sync(self, capabilitylist_data):
        """
        ``build step 6`` :samp:`Update description with newly created capabilitylist`

        :param capabilitylist_data: :class:`SitemapData` over the newly created capabilitylist
        :return: :class:`SitemapData` over updated description
        """
        src_desc_path = self.param.abs_description_path()
        well_known_dir = os.path.dirname(src_desc_path)
        os.makedirs(well_known_dir, exist_ok=True)

        src_description = SourceDescription()
        if os.path.exists(src_desc_path):
            src_description = self.read_sitemap(src_desc_path, src_description)

        src_description.add(Resource(uri=capabilitylist_data.uri, capability=Capability.capabilitylist.name),
                            replace=True)
        sitemap_data = SitemapData(len(src_description), -1, self.param.description_url(), src_desc_path,
                                   Capability.description.name)
        if self.param.is_saving_sitemaps:
            self.save_sitemap(src_description, src_desc_path)
            sitemap_data.document_saved = True

        self.observers_inform(self, ExecutorEvent.completed_document, document=src_description, sitemap_data=sitemap_data)
        return sitemap_data
    # # Execution steps - end

    def clear_metadata_dir(self):
        ok = self.observers_confirm(self, ExecutorEvent.clear_metadata_directory, metadata_dir=self.param.abs_metadata_dir())
        if not ok:
            raise ObserverInterruptException("Process interrupted by observer: event: %s, metadata directory: %s"
                                             % (ExecutorEvent.clear_metadata_directory, self.param.abs_metadata_dir()))
        xml_files = glob(self.param.abs_metadata_path("*.xml"))
        for xml_file in xml_files:
            os.remove(xml_file)

        wellknown = os.path.join(self.param.abs_metadata_dir(), WELL_KNOWN_PATH)
        if os.path.exists(wellknown):
            os.remove(wellknown)

    def resource_generator(self) -> iter:

        def generator(resource_metadata: [Resource], count=0) -> [int, Resource]:
            for res in resource_metadata:
                if not isinstance(res, Resource):
                    LOG.warning("Resource metadata is not of type Resource. Received type: %s" % type(res))
                    #filename = str(filename)

                count += 1
                if not res.length:
                    LOG.warning("Resource %s does not have the mandatory parameter length." % count)
                if not res.md5:
                    LOG.warning("Resource %s does not have the mandatory parameter md5." % count)
                if not res.lastmod:
                    LOG.warning("Resource %s does not have the mandatory parameter lastmod." % count)
                if not res.mime_type:
                    LOG.warning("Resource %s does not have the mandatory parameter mimetype." % count)
                yield count, res

                #file = os.path.abspath(filename)
                #if not os.path.exists(file):
                #    LOG.warning("File does not exist: %s" % file)
                #elif os.path.isdir(file):
                #    for cr, rsc in generator(self.walk_directories(file), count=count):
                #        yield cr, rsc
                #        count = cr
                #elif os.path.isfile(file):
                #    count += 1
                #    path = os.path.relpath(file, self.param.resource_dir)
                #    uri = self.param.url_prefix + defaults.sanitize_url_path(path)
                #    stat = os.stat(file)
                #    resource = Resource(uri=uri, length=stat.st_size,
                #                        lastmod=defaults.w3c_datetime(stat.st_ctime),
                #                        md5=defaults.md5_for_file(file),
                #                        mime_type=defaults.mime_type(file))
                #    yield count, resource
                #    self.observers_inform(self, ExecutorEvent.created_resource, resource=resource,
                #                          count=count, file=file)
                #else:
                #    LOG.warning("Not a regular file: %s" % file)

        return generator

    def walk_directories(self, *directories) -> [str]:
        for directory in directories:
            abs_dir = os.path.abspath(directory)
            self.observers_inform(self, ExecutorEvent.start_file_search, directory=abs_dir)
            for root, _directories, _filenames in os.walk(abs_dir):
                for filename in _filenames:
                    file = os.path.join(root, filename)
                    yield file

    def find_ordinal(self, capability):
        rs_files = sorted(glob(self.param.abs_metadata_path(capability + "_*.xml")))
        if len(rs_files) == 0:
            return -1
        else:
            filename = os.path.basename(rs_files[len(rs_files) - 1])
            digits = re.findall("\d+", filename)
            return int(digits[0]) if len(digits) > 0 else 0

    def format_ordinal(self, ordinal):
        # prepends '_' before zfill to distinguish between indexes (*list-index.xml) and regular lists (*list_001.xml)
        return "_" + str(ordinal).zfill(self.param.zero_fill_filename)

    def finish_sitemap(self, ordinal, sitemap, doc_start=None, doc_end=None) -> SitemapData:
        capability_name = sitemap.capability_name
        file_name = capability_name
        if sitemap.sitemapindex:
            file_name += "-index"
        elif ordinal >= 0:
            file_name += self.format_ordinal(ordinal)

        file_name += ".xml"

        path = self.param.abs_metadata_path(file_name)
        url = self.param.uri_from_path(path)
        sitemap.link_set(rel="up", href=self.current_rel_up_for(sitemap))
        sitemap_data = SitemapData(len(sitemap), ordinal, url, path, capability_name)
        sitemap_data.doc_start = doc_start
        sitemap_data.doc_end = doc_end if doc_end else defaults.w3c_now()

        if self.param.is_saving_sitemaps:
            sitemap.pretty_xml = self.param.is_saving_pretty_xml
            self.save_sitemap(sitemap, path)
            sitemap_data.document_saved = True

        self.observers_inform(self, ExecutorEvent.completed_document, document=sitemap, sitemap_data=sitemap_data)
        return sitemap_data

    def current_rel_up_for(self, sitemap):
        if sitemap.capability_name == Capability.capabilitylist.name:
            return self.param.description_url()
        else:
            return self.param.capabilitylist_url()

    def update_rel_index(self, index_url, path):
        sitemap = self.read_sitemap(path)
        sitemap.link_set(rel="index", href=index_url)
        self.save_sitemap(sitemap, path)

    def save_sitemap(self, sitemap, path):
        sitemap.pretty_xml = self.param.is_saving_pretty_xml
        # writing the string sitemap.as_xml() to disk results in encoding=ASCII on some systems.
        # due to https://docs.python.org/3.4/library/xml.etree.elementtree.html#write
        sitemap.write(path)

    def read_sitemap(self, path, sitemap=None):
        if sitemap is None:
            sitemap = ListBaseWithIndex()
        with open(path, "r", encoding="utf-8") as file:
            sm = Sitemap()
            sm.parse_xml(file, resources=sitemap)
        return sitemap