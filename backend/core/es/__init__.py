import os 
from elasticsearch import helpers,Elasticsearch
import elasticsearch

INDEX_NAME = os.environ["INDEX_NAME"]
PAGE_INDEX_NAME = os.environ["PAGE_INDEX_NAME"]

ES_HOST = os.environ["ES_HOST"]
es = Elasticsearch(hosts=[ES_HOST])

def search_files(query=None, params={}): 
    must_filters = [{"match": {
            "text_raw": {
              "query": query,
              "analyzer": "synonym"
            }
            }}, {"match": {
            "text_raw": {
              "query": query,
              "analyzer": "custom"
            }
            }}]
    if params != {}: 
        for key in params: 
            must_filters.append( {"match" : {"metadata.{}".format(key): params[key]}})
    
    query =  {"bool": {"must": must_filters}}

    body = {"_source": ["file_name", "text", "page", "file_id"], 
            "size": 5,
            "query": query,
            "highlight": {
                "fragment_size": 150,
                "require_field_match": False,
                "fields": {
                "text_raw": {"force_source" : True},
                        "text": {"force_source" : True}
                }
             }}

    print(body)
    response = es.search(
                    index=PAGE_INDEX_NAME,
                    body=body
                )
    return response['hits']['hits']

def search_sections(query=None, params={}): 
    must_filters = [{"match": {
        "text_raw": {
            "query": query,
            "analyzer": "synonym"
        }
        }}, {"match": {
        "text_raw": {
            "query": query,
            "analyzer": "custom"
        }
        }}]
    if params != {}: 
        for key in params: 
            must_filters.append( {"match" : {"metadata.{}".format(key): params[key]}})

    query =  {"bool": {"must": must_filters}}

    body = {"_source": ["file_name", "text", "page", "file_id", "component"], 
            "size": 5,
            "query": query,
            "highlight": {
                "fragment_size": 120,
                "require_field_match": False,
                "fields": {
                "text_raw": {"force_source" : True},
                        "text": {"force_source" : True}
                }
             }}

    response = es.search(
                    index=INDEX_NAME,
                    body=body
                )
    return response['hits']['hits']