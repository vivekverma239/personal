import os 
from core.pdf_parser import parse
from core.pdf_parser.poppler_parser_v2 import parse_pdf_poppler

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, pre_delete  # importing the built-in signal
from core.models import SearchFile
from core.utils.encoder import encode_questions, encode_responses
from elasticsearch import helpers,Elasticsearch
import elasticsearch

INDEX_NAME = os.environ["INDEX_NAME"]
PAGE_INDEX_NAME = os.environ["PAGE_INDEX_NAME"]

ES_HOST = os.environ["ES_HOST"]
es = Elasticsearch(hosts=[ES_HOST])

def index_file(file_id, file_name, contexts, metadata):
    actions = []
    # use_texts = encode_use(texts)
    qa_use_texts = encode_responses([i["text"] for i in contexts])

    for idx, context in enumerate(contexts):
        doc = {
                "file_id": file_id,
                "file_name" : file_name,
                "text": context["text"],
                "page": context["page"],
                "component": context,
                "metadata": metadata,
                "boxes": context["merged"],
                # "use_vector": use_texts[idx],
                "use_qa_vector": qa_use_texts[idx],
            }
        actions.append({"_index": INDEX_NAME,
                        "_id": "{}_{}".format(file_id, idx), 
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

def index_file_pages(file_id, file_name, parsed_data, metadata):
    actions = []
    if 'pages'  in parsed_data: 
        for page in parsed_data['pages']: 
            page_data = parsed_data['pages'][page]
            text = "\n".join([i.get('text', '') for i in page_data['components']])
            # use_texts = encode_use([text])
            # qa_use_texts = encode_responses([text])
            doc = {
                    "file_id": file_id,
                    "file_name" : file_name,
                    "text": text,
                    "page": page,
                    "metadata": metadata
                    # "use_vector": use_texts[0],
                    # "use_qa_vector": qa_use_texts[0],
                }
            actions.append({"_index": PAGE_INDEX_NAME,
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


@receiver(post_save, sender=SearchFile)
def parse_signal(sender, instance, **kwargs):
    if instance.status == 'pending':
        instance.parsed_data = parse_pdf_poppler(instance.file.path)
        # components = [] 
        # for page in instance.parsed_data['pages']:
        #     for component in instance.parsed_data['pages'][page]['components']:
        #         component["page"] = page
        #         components.append(component)
        instance.status = 'done'
        index_file(str(instance.id), instance.name, instance.parsed_data["contexts"], instance.metadata)
        # index_file_pages(str(instance.id), instance.name, instance.parsed_data, instance.metadata)
        instance.save()
    