from datetime import datetime

from elasticsearch import Elasticsearch

from resourcesync.generators.elastic.elastic_parameters import ElasticParameters
from resourcesync.generators.elastic.model.change_doc import ChangeDoc
from resourcesync.generators.elastic.model.location import Location
from resourcesync.generators.elastic.model.resource_doc import ResourceDoc


def location_query(resource_set, location: Location):
    return {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {"resource_set": resource_set}
                    },
                    {
                        "nested": {
                            "path": "location",
                            "query": {
                                "bool": {
                                    "must": [
                                        {
                                            "term": {"location.type": location.loc_type}
                                         },
                                        {
                                            "term": {"location.value": location.value}
                                        }
                                    ]
                                }
                            }

                        }
                    }
                ]
            }
        }
    }


def resource_set_query(resource_set):
    return {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {"resource_set": resource_set}
                    }
                ]
            }
        }
    }


def resync_id_query(resource_set, resync_id):
    return {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {"resource_set": resource_set}
                    },
                    {
                        "term": {"resync_id": resync_id}
                    }
                ]
            }
        }
    }


class ResourceAlreadyExistsException(TypeError):
    pass


class DuplicateResourceException(TypeError):
    pass


class ResourceNotFound(TypeError):
    pass


class ElasticQueryManager:
    def __init__(self, host: str, port: str):
        self._host = host
        self._port = port
        self._instance = self.es_instance()

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    def resource_exists(self, index, doc_type, resource_set, location):
        return False if self.get_document_by_location(index=index, doc_type=doc_type,
                                                      resource_set=resource_set, location=location) is None else True

    def get_document_by_location(self, index, doc_type, resource_set, location: Location):
        query = location_query(resource_set=resource_set, location=location)
        result = self._instance.search(index=index, doc_type=doc_type, body=query)
        hits = [ResourceDoc.as_resource_doc(hit['_source']) for hit in result['hits']['hits']]
        if len(hits) == 0:
            return None
        elif len(hits) > 1:
            # this should not happen
            raise DuplicateResourceException('Error: more than one resource with location: %s' % location.to_dict())
        elif len(hits) == 1:
            return hits[0]

    def get_document_by_elastic_id(self, index, doc_type, elastic_id):
        return self._instance.get(index=index, doc_type=doc_type, id=elastic_id, ignore=404)

    def es_instance(self) -> Elasticsearch:
        return Elasticsearch([{"host": self.host, "port": self.port}], timeout=30, max_retries=10,
                             retry_on_timeout=True)

    def create_index(self, index, mapping):
        return self._instance.indices.create(index=index, body=mapping, ignore=400)

    def delete_index(self, index):
        return self._instance.indices.delete(index=index, ignore=404)

    def delete_document(self, index, doc_type, elastic_id):
        return self._instance.delete(index=index, doc_type=doc_type, id=elastic_id, ignore=404)

    def index_document(self, index, doc_type, doc, elastic_id=None, op_type='index'):
        return self._instance.index(index=index, doc_type=doc_type, id=elastic_id, body=doc, op_type=op_type,
                                    ignore=409)

    def delete_document_by_location(self, index, resource_doc_type, resource_set, location: Location):
        query = location_query(resource_set=resource_set, location=location)
        return self._instance.delete_by_query(index=index, doc_type=resource_doc_type, body=query)

    def delete_all_index_set_type_docs(self, index, doc_type, resource_set):
        query = resource_set_query(resource_set)
        self._instance.delete_by_query(index=index, doc_type=doc_type, body=query)

    def refresh_index(self, index):
        return self._instance.indices.refresh(index=index)

    def scan_and_scroll(self, index, doc_type, query, max_items_in_list, max_result_window):
        result_size = max_items_in_list
        n_iter = 1
        c_iter = 0
        # index.max_result_window in Elasticsearch controls the max number of results returned from a query.
        # we can either increase it to 50k in order to match the sitemaps pagination requirements or not
        # in the latter case, we have to bulk the number of items that we want to put into each resourcelist chunk
        if max_items_in_list > max_result_window:
            n = max_items_in_list / max_result_window
            n_iter = int(n)
            result_size = max_result_window

        page = self._instance.search(index=index, doc_type=doc_type, scroll='2m', size=result_size, body=query)
        sid = page['_scroll_id']
        # total_size = page['hits']['total']
        scroll_size = len(page['hits']['hits'])
        bulk = page['hits']['hits']
        c_iter += 1
        # if c_iter and n_iter control the number of iteration we need to perform in order to yield a bulk of
        #  (at most) self.para.max_items_in_list
        if c_iter >= n_iter or scroll_size < result_size:
            c_iter = 0
            yield bulk
            bulk = []

        while scroll_size > 0:
            page = self._instance.scroll(scroll_id=sid, scroll='2m')
            # Update the scroll ID
            sid = page['_scroll_id']
            # Get the number of results that we returned in the last scroll
            scroll_size = len(page['hits']['hits'])
            bulk.extend(page['hits']['hits'])
            c_iter += 1
            if c_iter >= n_iter or scroll_size < result_size:
                c_iter = 0
                yield bulk
                bulk = []

    # high level resource handling
    def create_or_update_resource(self, params: ElasticParameters, elastic_id, location, length, md5, mime, lastmod,
                                  ln=None, record_change=True):

        index = params.elastic_index

        resource_doc = ResourceDoc(resync_id=elastic_id, resource_set=params.resource_set, location=location,
                                   length=length, md5=md5, mime=mime, lastmod=lastmod,
                                   ln=ln, timestamp=self.formatted_date(datetime.now()))
        response = self.index_document(index=index, doc_type=params.elastic_resource_doc_type,
                                       doc=resource_doc.to_dict(), elastic_id=elastic_id, op_type='index')

        if response.get('error') is None and record_change:
            if response.get('created') is False:
                change = 'created'
            else:
                change = 'updated'

            change_doc = ChangeDoc(resource_set=params.resource_set,
                                   location=location, lastmod=lastmod, change=change,
                                   datetime=self.formatted_date(datetime.now()),
                                   timestamp=self.formatted_date(datetime.now()))
            self.index_document(index=index, doc_type=params.elastic_change_doc_type, doc=change_doc.to_dict())

        return response

    def create_resource(self, params: ElasticParameters, elastic_id, location, length, md5, mime, lastmod,
                        ln=None, record_change=True):

        index = params.elastic_index

        resource_doc = ResourceDoc(resync_id=elastic_id, resource_set=params.resource_set, location=location,
                                   length=length, md5=md5, mime=mime, lastmod=lastmod, ln=ln)
        response = self.index_document(index=index, doc_type=params.elastic_resource_doc_type,
                                       doc=resource_doc.to_dict(), elastic_id=elastic_id, op_type='create')

        if response.get('error') is None and record_change:
            change_doc = ChangeDoc(resource_set=params.resource_set,
                                   location=location, lastmod=lastmod, change='created',
                                   datetime=self.formatted_date(datetime.now()),
                                   timestamp=self.formatted_date(datetime.now()))
            self.index_document(index=index, doc_type=params.elastic_change_doc_type, doc=change_doc.to_dict())

        return response

    def update_resource(self, params: ElasticParameters, elastic_id, location, length, md5, mime, lastmod,
                        ln=None, record_change=True):

        index = params.elastic_index

        resource_doc = ResourceDoc(resync_id=elastic_id, resource_set=params.resource_set, location=location,
                                   length=length, md5=md5, mime=mime, lastmod=lastmod, ln=ln)
        response = self.index_document(index=index, doc_type=params.elastic_resource_doc_type,
                                       doc=resource_doc.to_dict(), elastic_id=elastic_id, op_type='index')

        if response.get('error') is None and record_change:
            change_doc = ChangeDoc(resource_set=params.resource_set,
                                   location=location, lastmod=lastmod, change='updated',
                                   datetime=self.formatted_date(datetime.now()),
                                   timestamp=self.formatted_date(datetime.now()))
            self.index_document(index=index, doc_type=params.elastic_change_doc_type, doc=change_doc.to_dict())

        return response

    def delete_resource(self, params: ElasticParameters, elastic_id, location: Location, record_change=True):

        index = params.elastic_index

        response = self.delete_document(index=index, doc_type=params.elastic_resource_doc_type,
                                        elastic_id=elastic_id)

        if response.get('error') is None and record_change:
            change_doc = ChangeDoc(resource_set=params.resource_set,
                                   location=location, change='deleted',
                                   datetime=self.formatted_date(datetime.now()),
                                   timestamp=self.formatted_date(datetime.now()))
            self.index_document(index=index, doc_type=params.elastic_change_doc_type, doc=change_doc.to_dict())

        return response

    def get_resource(self, params: ElasticParameters, elastic_id):

        index = params.elastic_index

        response = self.get_document_by_elastic_id(index=index, doc_type=params.elastic_resource_doc_type,
                                                   elastic_id=elastic_id)

        return response

    @staticmethod
    def formatted_date(d: datetime):
        return d.strftime("%Y-%m-%dT%H:%M:%SZ")

