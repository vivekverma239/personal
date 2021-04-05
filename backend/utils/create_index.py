from elasticsearch import Elasticsearch
import elasticsearch
import os 

SETTINGS = {
  "settings": {
    "index": {
      "analysis": {
        "analyzer": {
          "custom": {
            "tokenizer": "standard",
            "filter": [
              "lowercase",
              "english_stop",
              "porter_stem"
            ]
          },
          "synonym": {
            "tokenizer": "standard",
            "filter": [
              "lowercase",
              "synonym",
              "porter_stem"
            ]
          }
        },
        "filter": {
         "english_stop":{
               "type":"stop",
               "stopwords":"_english_"
            },
          "synonym": {
            "type": "synonym_graph",
            "synonyms_path": "../data/synonyms_v3.txt"
          }
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "file_id": {
        "type": "keyword",
      },
      "file_name": {
        "type": "keyword",
      },  
      "page": {
        "type": "keyword",
      },  
      "text": {
        "type": "text",
        "copy_to": ["text_raw" , "text_parsed"]
      }, 
      "text_parsed": {
        "type": "text",
        "analyzer": "synonym",
      },
      "text_raw" : {
        "type": "text",
        "analyzer": "custom"
      },      "use_vector": {
        "type": "dense_vector",
        "dims": 512
    }, 
      "use_qa_vector": {
        "type": "dense_vector",
        "dims": 512
    }
    }
  }
}


PAGE_SETTINGS = {
  "settings": {
    "index": {
      "analysis": {
        "analyzer": {
          "custom": {
            "tokenizer": "standard",
            "filter": [
              "lowercase",
              "english_stop",
              "stemmer"
            ]
          },
          "synonym": {
            "tokenizer": "standard",
            "filter": [
              "lowercase",
              "synonym"
            ]
          }
        },
        "filter": {
         "english_stop":{
               "type":"stop",
               "stopwords":"_english_"
            },
          "synonym": {
            "type": "synonym_graph",
            "synonyms_path": "../data/synonyms.txt"
          }
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "file_id": {
        "type": "keyword",
      },
      "file_name": {
        "type": "keyword",
      },  
      "page": {
        "type": "keyword",
      },  
      "text": {
        "type": "text",
        "copy_to": ["text_raw" , "text_parsed"]
      }, 
      "text_parsed": {
        "type": "text",
        "analyzer": "synonym",
      },
      "text_raw" : {
        "type": "text",
        "analyzer": "custom"
      },
      "use_vector": {
        "type": "dense_vector",
        "dims": 512
    }, 
      "use_qa_vector": {
        "type": "dense_vector",
        "dims": 512
    }
    }
  }
}


ES_INDEX = os.environ["INDEX_NAME"]
PAGE_ES_INDEX = os.environ["PAGE_INDEX_NAME"]
TEST_ES_INDEX = "test_index_v5"

ES_HOST = os.environ["ES_HOST"]

def main():
    es = Elasticsearch(hosts=[ES_HOST])
    index = elasticsearch.client.IndicesClient(es)
    if not es.indices.exists(index=ES_INDEX):
      index.create(ES_INDEX, body=SETTINGS)
    if not es.indices.exists(index=PAGE_ES_INDEX):
      index.create(PAGE_ES_INDEX, body=SETTINGS)
    if not es.indices.exists(index=TEST_ES_INDEX):
      index.create(TEST_ES_INDEX, body=SETTINGS)
    return True

if __name__ == '__main__':
    print(main())