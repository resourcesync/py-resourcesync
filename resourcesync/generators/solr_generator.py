# -*- coding: utf-8 -*-

"""
:samp:`A Solr Generator.`
"""

from resourcesync.core.generator import Generator
from hashlib import md5
from resync import Resource
from requests import get
from urllib.parse import quote

class SolrGenerator(Generator):

    """Generator class for using ResourceSync with Solr results sets.
    This generator expects a dictionary supplied via the `params` kwarg with
    the following keys set:

    solr_base_url         the base URL for OAI-PMH requests, to which query
i                         parameters are appended to form the full request URL
    solr_query            a pre-formulated solr query 
    solr_params           other GET parameters for Solr (wt, nextCursorMark, etc)
    metadata_identifier   label for metadata identifier in Solr results set
    metadata_disseminator an optional parameter if the metadata_identifier needfs to be paired 
                          with a URL in order to dereference and retrieve full metadata record 
    metadata_timestamp    the timestamp label for this Solr index
    metadata_type         the metadata type that is returned by de-referencing the value of the 
                          metadata_identifier field
    """

    def __init__(self, params=None, rsxml=None):

        Generator.__init__(self, params, rsxml=rsxml)

    def generate(self):
        results = self.get_queryset()
        return list(map(self.solr_results_to_resourcesync_resource, results))

    def get_queryset(self):

      resultSet = []
      # Constants
      metadataUriBase = self.params['metadata_disseminator']
      timestamp_label = self.params['metadata_timestamp']
      id_label = self.params['metadata_identifier']

      allFound = False
      pagingCursor = ''

      while not(allFound):
        lastCursor = pagingCursor

        searchUri = self.params['solr_base_url'] + quote(self.params['solr_query'], safe='') + self.params['solr_params']
        # print (searchUri)

        if not (pagingCursor == ''):
           searchUri = searchUri.replace('_*_',pagingCursor)
        else:
          searchUri = searchUri.replace('_*_','*')

        resp = get(searchUri)
        response = eval(resp.text)

        try:
          pagingCursor = response['nextCursorMark']
        except:
          pagingCursor = lastCursor

        if pagingCursor == lastCursor:
          allFound = True
 
        try:
            for document in response['response']['docs']:
              resultObj = {}
              resultObj['timestamp'] = document[timestamp_label]
              resultObj['id'] = document[id_label]
              resultSet.append(resultObj)
        except:
            pass

      return resultSet

    def solr_results_to_resourcesync_resource(self,  a_result):

        if not self.params['metadata_disseminator']=='':
          uri = self.params['metadata_disseminator'].replace('_ID_', a_result['id'])
        else:
          uri = a_result['id']
        # self.params['metadata_type'])
        lastmod    = a_result['timestamp']

        # do a GET request for each record to retrieve the 'content-length'
        r      = get(uri)
        length = len(r.content)

        # compute md5 of the metadata record
        m       = md5()
        element = str(r.content).encode('utf-8')
        m.update(element)

        return Resource(
            uri=uri,
            lastmod=lastmod,
            md5=m.hexdigest(),
            length=length,
            mime_type="text/xml")

    def main(self):
      print (self.generate())

if __name__ == '__main__':
  sg = SolrGenerator()
  #sg.main()
  rs = ResourceSync(generator=sg, strategy="resourcelist")
  rs.execute()
