import os 
import time
import json 
from elasticsearch import helpers,Elasticsearch
import elasticsearch

import tensorflow_hub as hub
import numpy as np
import tensorflow as tf 
from tqdm import tqdm 
TEST_ES_INDEX = "test_index_v5"
import binascii


def generate() -> str:
    timestamp = "{:x}".format(int(time.time()))
    rest = binascii.b2a_hex(os.urandom(8)).decode("ascii")
    return timestamp + rest



module = hub.load('https://tfhub.dev/google/universal-sentence-encoder-qa/3')
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

def encode_questions(questions):
    question_embeddings = module.signatures['question_encoder'](
                tf.constant(questions))
    return question_embeddings['outputs'].numpy()

def encode_responses(responses):
    response_embeddings = module.signatures['response_encoder'](
            input=tf.constant(responses),
            context=tf.constant(responses))
    return response_embeddings['outputs'].numpy()

def encode_use(sentences):
    return embed(sentences).numpy()

ES_HOST = os.environ["ES_HOST"]
es = Elasticsearch(hosts=[ES_HOST])

def index_file_pages(file_id, file_name, data, metadata):
    actions = []
    intent = data['intent']
    responses = data['response']
    for idx, response in enumerate(responses): 
        if len(response) ==0 or len(response[0]['text']) < 50 : 
            continue
        doc = {
                "file_id": file_id,
                "file_name" : file_name,
                "text": response[0]['text'],
                "metadata": metadata,
                # "use_qa_vector" : encode_responses([response[0]['text']])[0]
            }
        actions.append({"_index": TEST_ES_INDEX,
                        "_id": "{}_{}".format(file_id, generate()), 
                        "_source": doc})

    error = ""
    try: 
        res = helpers.bulk(es, actions)
    # except elasticsearch.exceptions as e: 
    except Exception as e: 
        error = e.error
        print("Exception")
        import traceback
        traceback.print_exc()

def main(): 
    # data = json.loads(open("data/export.json").read())
    data = json.loads(open("data/pdf_data.json").read())

    count = 0 
    for project in tqdm(data): 
        project_data = data[project]
        for idx, item in tqdm(list(enumerate(project_data))):
            intent = item['intent']
            index_file_pages(project, intent, item, {'project_name': project})

if __name__ == '__main__':
    main()