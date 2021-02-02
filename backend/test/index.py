import os 
import json 
from elasticsearch import helpers,Elasticsearch
import elasticsearch
from tqdm import tqdm 
TEST_ES_INDEX = "test_index"

ES_HOST = os.environ["ES_HOST"]
es = Elasticsearch(hosts=[ES_HOST])

def index_file_pages(file_id, file_name, data, metadata):
    actions = []
    intent = data['intent']
    responses = data['response']
    if idx, response  in enumerate(responses): 
        doc = {
                "file_id": file_id,
                "file_name" : file_name,
                "text": response['text'],
                "metadata": metadata
                # "use_vector": use_texts[0],
                # "use_qa_vector": qa_use_texts[0],
            }
        actions.append({"_index": TEST_ES_INDEX,
                        "_id": "{}_{}".format(file_id, page), 
                        "_source": doc})

        error = ""
        try: 
            res = helpers.bulk(es, actions)
        # except elasticsearch.exceptions as e: 
        except Exception as e: 
            error = e.error
            print("Exception")
            import traceback 
            print(traceback.print_exc())


def main(): 
    data = json.loads(open("data/export.json").read())
    for project in data: 
        project_data = data[project]
        for item in project_data:
            intent = item['intent']
            index_file_pages(project, intent, item, {'project_name': project_data})