import os 
import time
import json 
import pandas as pd 
from elasticsearch import helpers,Elasticsearch
import elasticsearch
from tqdm import tqdm 
import tensorflow_hub as hub
import tensorflow as tf 
import torch
from transformers import BertForQuestionAnswering, BertForSequenceClassification
from transformers import BertTokenizer
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

TEST_ES_INDEX = "test_index_v4"
import binascii

ES_HOST = os.environ["ES_HOST"]
es = Elasticsearch(hosts=[ES_HOST])

module = hub.load('https://tfhub.dev/google/universal-sentence-encoder-qa/3')
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

custom = BertForSequenceClassification.from_pretrained('data/models/RERANK_MODEL_DIR/')
custom_tokenizer = BertTokenizer.from_pretrained('data/models/RERANK_MODEL_DIR/')


def encode_questions(questions):
    question_embeddings = module.signatures['question_encoder'](
                tf.constant(questions))
    return question_embeddings['outputs'].numpy()

def search_sections(query=None, params={}, size=5): 
    must_filters = [{"match": {
        "text_parsed": {
            "query": query,
            "analyzer": "synonym"
        }
        }}, {"match": {
        "text_raw": {
            "query": query,
            "analyzer": "custom"
        }
        }}]
    # must_filters = [{"match": {
    #     "text_raw": {
    #         "query": query,
    #         "analyzer": "custom"
    #     }
    #     }}]
    if params != {}: 
        for key in params: 
            must_filters.append( {"match" : {"metadata.{}".format(key): params[key]}})

    query =  {"bool": {"must": must_filters}}

    body = {"_source": ["file_name", "text", "page", "file_id", "component"], 
            "size": size,
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
                    index=TEST_ES_INDEX,
                    body=body
                )
    return response['hits']['hits']


def validate(query=None, intent=None, params={}, size=5): 
    # must_filters = [{"match": {
    #     "text_raw": {
    #         "query": query,
    #         "analyzer": "synonym"
    #     }
    #     }}, {"match": {
    #     "text_raw": {
    #         "query": query,
    #         "analyzer": "custom"
    #     }
    #     }}]
    must_filters = [{"match": {
        "text_raw": {
            "query": query,
            "analyzer": "custom"
        }
        }}, {"match_phrase": {
        "file_name":intent
        }}]
    if params != {}: 
        for key in params: 
            must_filters.append( {"match" : {"metadata.{}".format(key): params[key]}})

    query =  {"bool": {"must": must_filters}}

    body = {"_source": ["file_name", "text", "page", "file_id", "component"], 
            "size": size,
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
                    index=TEST_ES_INDEX,
                    body=body
                )
    # print(response['hits']['total'])
    return response['hits']['total']['value'] > 0, response['hits']['hits']

def search_sections_use(query=None, params={}, size=5): 
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
    vector = encode_questions([query])[0]
    query =  {"bool": {"must": must_filters}}
    body = {"_source": ["file_name", "text", "page", "file_id", "component"], 
            "size": size,
            "query": {
                "script_score" : 
                    {"query": query,
                     "script": {
                            "source": "cosineSimilarity(params.query_vector, doc['use_qa_vector']) + 1.0",
                            "params": {
                            "query_vector": vector.tolist()
                            }
                        }
                    }
            },
            "highlight": {
                "fragment_size": 120,
                "require_field_match": False,
                "fields": {
                "text_raw": {"force_source" : True},
                        "text": {"force_source" : True}
                }
             }}
    response = es.search(
                    index=TEST_ES_INDEX,
                    body=body
                )
    return response['hits']['hits']


def search_classifier(question, responses):
        pairs = [(question, response) for response in responses]

        input = custom_tokenizer(pairs, return_tensors='pt', 
                    padding=True, add_special_tokens=True, 
                    return_token_type_ids=True,  truncation=True, max_length=256)

        # Report how long the input sequence is.
        # print(input)
        scores = custom(**input)[0] # The segment IDs to differentiate question from answer_text
        # ======== Reconstruct Answer ========
        # Find the tokens with the highest `start` and `end` scores.
        # print(input, scores)
        # scores = torch.max(scores, dim=-1)[0]
        # print(scores)
        return scores[:, 1].detach().numpy()

def reorder_custom(query, results):
    if len(results) != 0:
        try:
            responses = [i['_source']['text'] for i in results]
            scores = search_classifier(query, responses)
            for idx, response in enumerate(responses): 
                results[idx]['ml_score'] = scores[idx]
            return list(sorted(results, key=lambda x: -x['ml_score']))

        except:
            import traceback
            print(traceback.print_exc())
            # print(query, results)
            return []
    else:
        return []

def main(): 
    # data = json.loads(open("data/export.json").read())
    data = json.loads(open("data/pdf_data.json").read())

    count = 0 
    result_data = [{'project name': name} for name in data]
    for proj_idx, project in tqdm(enumerate(data)): 
        project_data = data[project]
        total = 0 
        errors = []
        correct = {1:0 , 2:0, 3:0, 5 : 0, 10: 0, 15: 0, 20:0, 25:0, 'total': 0}
        
        for idx, item in tqdm(list(enumerate(project_data))):
            valid_responses = 0
            for response in item['response']:
                if len(response) > 0 and len(response[0]['text']) > 50 : 
                    valid_responses += 1 
            
            if valid_responses == 0 : 
                continue
            for utterance in item['utterance']:
                results = search_sections(utterance, {'project_name': project}, size=25)
                # results = search_sections_use(utterance, {'project_name': project}, size=5)
                total += 1
                found = False
                # results = reorder_custom(utterance, results)
                validate_flag, valid_res = validate(utterance, item["intent"], {'project_name': project}, size=25)
                for idx, result in enumerate(results): 
                    if result['_source']['file_name'] == item['intent']:
                        found = True
                        if idx < 1: 
                            correct[1] += 1
                            correct[2] += 1
                            correct[3] += 1
                            correct[5] += 1
                            correct[10] += 1
                            correct[15] += 1
                            correct[20] += 1
                            correct[25] += 1
                            found = True
                            break
                        elif idx < 2: 
                            correct[2] += 1
                            correct[3] += 1
                            correct[5] += 1
                            correct[10] += 1
                            correct[15] += 1
                            correct[20] += 1
                            correct[25] += 1
                            found = True
                            break
                        elif idx < 3: 
                            correct[3] += 1
                            correct[5] += 1
                            correct[10] += 1
                            correct[15] += 1
                            correct[20] += 1
                            correct[25] += 1
                            found = True
                            break
                        elif idx < 5: 
                            correct[5] += 1
                            correct[10] += 1
                            correct[15] += 1
                            correct[20] += 1
                            correct[25] += 1
                            found = True
                            break
                        elif idx < 10: 
                            correct[10] += 1
                            correct[15] += 1
                            correct[20] += 1
                            correct[25] += 1
                            found = True
                            break
                        elif idx < 15: 
                            correct[15] += 1
                            correct[20] += 1
                            correct[25] += 1
                            break
                        elif idx < 20: 
                            correct[20] += 1
                            correct[25] += 1
                            break
                        elif idx < 25: 
                            correct[25] += 1
                            break
                if validate_flag: 
                    correct['total'] += 1

                if not found: 
                    valid_item = valid_res[0]['_source']['text'] if validate_flag else ''
                    errors.append([item['intent'], utterance, valid_item.replace("\n", "#")])
        pd.DataFrame(errors, columns=['Intent', "Utterance", "response"]).to_csv("data/errors/{}.csv".format(project))
        if total > 0: 
            print(project)
            for key in correct:
                temp = result_data[proj_idx]
                temp["Accuracy@{}".format(key)] = correct[key] / total
                result_data[proj_idx] = temp
            print(temp)
    print(pd.DataFrame(result_data))
    # pd.DataFrame(result_data).to_csv('data/retriever_results.csv', index=False)
    # pd.DataFrame(result_data).to_csv('data/retriever_results_v2.csv', index=False)
    pd.DataFrame(result_data).to_csv('data/retriever_results_v3.csv', index=False)

    # pd.DataFrame(result_data).to_csv('data/retriever_results_stage2.csv', index=False)

if __name__ == '__main__':
    main()