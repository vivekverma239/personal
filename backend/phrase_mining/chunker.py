from nltk import word_tokenize, pos_tag, ne_chunk
from nltk import RegexpParser
from nltk import Tree
import pandas as pd
import json 
from tqdm import tqdm 
# NP = "NP: {(<V\w+>|<NN\w?>)+.*<NN\w?>}"
# chunker = RegexpParser(NP)

def get_continuous_chunks(text, chunk_func=ne_chunk):
    chunked = chunk_func(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []

    for subtree in chunked:
        if type(subtree) == Tree:
            current_chunk.append(" ".join([token for token, pos in subtree.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue

    return continuous_chunk

def main(): 
    entities = {}
    data = json.loads(open("data/export.json").read())
    count = 0 
    for project in data: 
        print(project)
        chunks = [] 
        for item in tqdm(data[project]):
            for utternace in item["utterance"]: 
                chunks.extend( get_continuous_chunks(utternace))
            for response in item["response"]:
                for temp in response: 
                    chunks.extend( get_continuous_chunks(temp["text"]))
        for chunk in chunks: 
            entities[chunk] = entities.get(chunk, 0) + 1
    with open("data/entities.json", "w") as file_: 
        file_.write(json.dumps(entities, indent=2))

if __name__ == '__main__': 
    main()


curl -XGET "http://es01:9200/bot_data_v1/_search?pretty=true" -H 'Content-Type: application/json' -d'{  "_source": ["intent", "utterance","category" , "version"],   "query": {    "bool": {      "must": [        {          "match": {            "intent": "defaultFallback"          }        },        {          "match": {            "utterance": "Laptop battery life reduced"          }        },        {          "match": {            "bot_id": "5de79232d79ec60504d6c68d"          }        }      ]    }  }}'