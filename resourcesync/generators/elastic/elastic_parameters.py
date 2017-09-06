class ElasticParameters:
    """
    :samp:`Extension of Parameters to support Elasticsearch-specific settings`
    """
    def __init__(self, **kwargs):
        self.resource_set = kwargs['resource_set']
        self.resource_root_dir = kwargs['resource_root_dir']
        self.elastic_host = kwargs['elastic_host']
        self.elastic_port = kwargs['elastic_port']
        self.elastic_index = kwargs['elastic_index']
        self.elastic_resource_doc_type = kwargs['elastic_resource_doc_type']
        self.elastic_change_doc_type = kwargs['elastic_change_doc_type']
        self.strategy = kwargs['strategy']
        self.max_items_in_list = kwargs['max_items_in_list']
        self.url_prefix = kwargs['url_prefix']


