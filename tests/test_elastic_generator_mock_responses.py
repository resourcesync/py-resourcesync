elastic_mock_responses = \
    [
        {
            "http://example.com:9200/resync-test/resource/_search?scroll=2m&size=2":
            """
            {
                "_scroll_id": "cXVlcnlUaGVuRmV0Y2g7NTs4MToyY1VUTG9rZlRFV29DUjZuSTVldjhBOzg0OjJjVVRMb2tmVEVXb0NSNm5JNWV2OEE7ODI6MmNVVExva2ZURVdvQ1I2bkk1ZXY4QTs4MzoyY1VUTG9rZlRFV29DUjZuSTVldjhBOzg1OjJjVVRMb2tmVEVXb0NSNm5JNWV2OEE7MDs=",
                "took": 6,
                "timed_out": false,
                "_shards": {
                    "total": 5,
                    "successful": 5,
                    "failed": 0
                },
                "hits": {
                    "total": 2,
                    "max_score": 3.1273298,
                    "hits": [
                        {
                            "_index": "resync-mock",
                            "_type": "resource",
                            "_id": "e3318e29d69865d5ad8e7532de473c427bc0ca44572c117158b7ee98cbccb4d5",
                            "_score": 3.1273298,
                            "_source": {
                                "resync_id": "e3318e29d69865d5ad8e7532de473c427bc0ca44572c117158b7ee98cbccb4d5",
                                "resource_set": "foo-set",
                                "location": {
                                    "type": "rel_path",
                                    "value": "data/foo/aHR0cDovL2FwaS5lbHNldmllci5jb20vY29udGVudC9hcnRpY2xlL3BpaS8wMDA1Mjc0NDY5OTA0NDA51208.json"
                                },
                                "length": 0,
                                "md5": "d41d8cd98f00b204e9800998ecf8427e",
                                "mime": "application/json",
                                "lastmod": "2017-04-13T10:53:28Z",
                                "ln": [
                                    {
                                        "href": {
                                            "type": "rel_path",
                                            "value": "data/foo/aHR0cDovL2FwaS5lbHNldmllci5jb20vY29udGVudC9hcnRpY2xlL3BpaS8wMDA1Mjc0NDY5OTA0NDA51208.pdf"
                                        },
                                        "rel": "describes",
                                        "mime": "application/pdf"
                                    }
                                ],
                                "timestamp": "2017-04-13T11:56:18Z"
                            }
                        },
                        {
                            "_index": "resync-mock",
                            "_type": "resource",
                            "_id": "d5ffabf41cbab8aae9bc1a07988cec017db2d587f217537688d72fe342fa35ec",
                            "_score": 3.1273298,
                            "_source": {
                                "resync_id": "d5ffabf41cbab8aae9bc1a07988cec017db2d587f217537688d72fe342fa35ec",
                                "resource_set": "foo-set",
                                "location": {
                                    "type": "rel_path",
                                    "value": "data/foo/aHR0cDovL2FwaS5lbHNldmllci5jb20vY29udGVudC9hcnRpY2xlL3BpaS8wMDA1Mjc0NDY5OTA0NDA51212.json"
                                },
                                "length": 0,
                                "md5": "d41d8cd98f00b204e9800998ecf8427e",
                                "mime": "application/json",
                                "lastmod": "2017-04-13T10:53:28Z",
                                "ln": [
                                    {
                                        "href": {
                                            "type": "rel_path",
                                            "value": "data/foo/aHR0cDovL2FwaS5lbHNldmllci5jb20vY29udGVudC9hcnRpY2xlL3BpaS8wMDA1Mjc0NDY5OTA0NDA51212.pdf"
                                        },
                                        "rel": "describes",
                                        "mime": "application/pdf"
                                    }
                                ],
                                "timestamp": "2017-04-13T11:56:18Z"
                            }
                        }
                    ]
                }
            }""",

            "http://example.com:9200/_search/scroll?scroll=2m&scroll_id"
            "=cXVlcnlUaGVuRmV0Y2g7MjA7MTc5NzYyNjY0OkhCVWNKUmhPUnUyeEhTYU9wb19rWFE7Mjg1OTI2MTY2Om1BZHQzUG5qUW1tckdVSXcxRGNDeHc7MTYyOTQwMDI3OkgtTlYxaEpMUks2Qk0xc0ZSTVRyX2c7MjU1MDEzMjMwOkcxcGNQQ283UktxYjBUMHhjNEJHbmc7Mjg1OTI2MTY3Om1BZHQzUG5qUW1tckdVSXcxRGNDeHc7MTYyOTQwMDI4OkgtTlYxaEpMUks2Qk0xc0ZSTVRyX2c7MjU1MDEzMjI5OkcxcGNQQ283UktxYjBUMHhjNEJHbmc7Mjg1OTI2MTY4Om1BZHQzUG5qUW1tckdVSXcxRGNDeHc7MTYyOTQwMDI5OkgtTlYxaEpMUks2Qk0xc0ZSTVRyX2c7MTc5NzYyNjY1OkhCVWNKUmhPUnUyeEhTYU9wb19rWFE7MjU1MDEzMjMxOkcxcGNQQ283UktxYjBUMHhjNEJHbmc7Mjg1OTI2MTY5Om1BZHQzUG5qUW1tckdVSXcxRGNDeHc7MTYyOTQwMDMwOkgtTlYxaEpMUks2Qk0xc0ZSTVRyX2c7MTc5NzYyNjY2OkhCVWNKUmhPUnUyeEhTYU9wb19rWFE7MjU1MDEzMjMyOkcxcGNQQ283UktxYjBUMHhjNEJHbmc7Mjg1OTI2MTcwOm1BZHQzUG5qUW1tckdVSXcxRGNDeHc7MTc5NzYyNjY3OkhCVWNKUmhPUnUyeEhTYU9wb19rWFE7MTYyOTQwMDMxOkgtTlYxaEpMUks2Qk0xc0ZSTVRyX2c7MTc5NzYyNjY4OkhCVWNKUmhPUnUyeEhTYU9wb19rWFE7MjU1MDEzMjMzOkcxcGNQQ283UktxYjBUMHhjNEJHbmc7MDs":
            """{
               "_scroll_id": "cXVlcnlUaGVuRmV0Y2g7MjA7MTc5NzYyNjY0OkhCVWNKUmhPUnUyeEhTYU9wb19rWFE7Mjg1OTI2MTY2Om1BZHQzUG5qUW1tckdVSXcxRGNDeHc7MTYyOTQwMDI3OkgtTlYxaEpMUks2Qk0xc0ZSTVRyX2c7MjU1MDEzMjMwOkcxcGNQQ283UktxYjBUMHhjNEJHbmc7Mjg1OTI2MTY3Om1BZHQzUG5qUW1tckdVSXcxRGNDeHc7MTYyOTQwMDI4OkgtTlYxaEpMUks2Qk0xc0ZSTVRyX2c7MjU1MDEzMjI5OkcxcGNQQ283UktxYjBUMHhjNEJHbmc7Mjg1OTI2MTY4Om1BZHQzUG5qUW1tckdVSXcxRGNDeHc7MTYyOTQwMDI5OkgtTlYxaEpMUks2Qk0xc0ZSTVRyX2c7MTc5NzYyNjY1OkhCVWNKUmhPUnUyeEhTYU9wb19rWFE7MjU1MDEzMjMxOkcxcGNQQ283UktxYjBUMHhjNEJHbmc7Mjg1OTI2MTY5Om1BZHQzUG5qUW1tckdVSXcxRGNDeHc7MTYyOTQwMDMwOkgtTlYxaEpMUks2Qk0xc0ZSTVRyX2c7MTc5NzYyNjY2OkhCVWNKUmhPUnUyeEhTYU9wb19rWFE7MjU1MDEzMjMyOkcxcGNQQ283UktxYjBUMHhjNEJHbmc7Mjg1OTI2MTcwOm1BZHQzUG5qUW1tckdVSXcxRGNDeHc7MTc5NzYyNjY3OkhCVWNKUmhPUnUyeEhTYU9wb19rWFE7MTYyOTQwMDMxOkgtTlYxaEpMUks2Qk0xc0ZSTVRyX2c7MTc5NzYyNjY4OkhCVWNKUmhPUnUyeEhTYU9wb19rWFE7MjU1MDEzMjMzOkcxcGNQQ283UktxYjBUMHhjNEJHbmc7MDs=",
               "took": 8,
               "timed_out": false,
               "_shards": {
                  "total": 20,
                  "successful": 20,
                  "failed": 0
               },
               "hits": {
                    "total": 0,
                    "max_score": null,
                    "hits": []
               }
            }"""
        }
    ]
