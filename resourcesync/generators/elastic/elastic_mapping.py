def elastic_mapping(resource_type, change_type):
    mapping = {
        "mappings": {
            resource_type: {
                "properties": {
                    "resync_id":{
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "location": {
                        "type": "nested",
                        "properties": {
                            "value": {
                                "type": "string",
                                "index": "not_analyzed"
                            },
                            "type": {
                                "type": "string",
                                "index": "not_analyzed"
                            }
                        }
                    },
                    "length": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "md5": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "mime": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "lastmod": {
                        "type": "date",
                        "format": "yyyy-MM-dd\'T\'HH:mm:ssZ"
                    },
                    "resource_set": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "ln": {
                        "type": "nested",
                        "index_name": "link",
                        "properties": {
                            "rel": {
                                "type": "string",
                                "index": "not_analyzed"
                            },
                            "href": {
                                "type": "nested",
                                "properties": {
                                    "value": {
                                        "type": "string",
                                        "index": "not_analyzed"
                                    },
                                    "type": {
                                        "type": "string",
                                        "index": "not_analyzed"
                                    }
                                }
                            },
                            "mime": {
                                "type": "string",
                                "index": "not_analyzed"
                            }
                        }
                    },
                    "timestamp": {
                        "type": "date",
                        "format": "yyyy-MM-dd\'T\'HH:mm:ssZ"
                    }
                }
            },
            change_type: {
                "properties": {
                    "location": {
                        "type": "nested",
                        "properties": {
                            "value": {
                                "type": "string",
                                "index": "not_analyzed"
                            },
                            "type": {
                                "type": "string",
                                "index": "not_analyzed"
                            }
                        }
                    },
                    "lastmod": {
                        "type": "date",
                        "format": "yyyy-MM-dd\'T\'HH:mm:ssZ"
                    },
                    "change": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "resource_set": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "datetime": {
                        "type": "date",
                        "format": "yyyy-MM-dd\'T\'HH:mm:ssZ"
                    },
                    "timestamp": {
                        "type": "date",
                        "format": "yyyy-MM-dd\'T\'HH:mm:ssZ"
                    }
                }
            }
        }
    }
    return mapping
