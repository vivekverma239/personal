from nltk import sent_tokenize
import torch 
import colorsys
import numpy as np
import tensorflow as tf
from transformers import BertForQuestionAnswering, BertForSequenceClassification
from transformers import BertTokenizer
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

# model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
# tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
# longformer = AutoTokenizer.from_pretrained("mrm8488/longformer-base-4096-finetuned-squadv2")
# long_tokenizer = AutoModelForQuestionAnswering.from_pretrained("mrm8488/longformer-base-4096-finetuned-squadv2")
custom = BertForSequenceClassification.from_pretrained('data/models/RERANK_MODEL_DIR/')
custom_tokenizer = BertTokenizer.from_pretrained('data/models/RERANK_MODEL_DIR/')

k = 5
stride = 2

def answer_question(question, answer_text):
    '''
    Takes a `question` string and an `answer_text` string (which contains the
    answer), and identifies the words within the `answer_text` that are the
    answer. Prints them out.
    '''
    # ======== Tokenize ========
    # Apply the tokenizer to the input text, treating them as a text-pair.
    input = tokenizer([(question, answer_text)], return_tensors='pt')

    # Report how long the input sequence is.

    start_scores, end_scores = model(**input) # The segment IDs to differentiate question from answer_text

    # ======== Reconstruct Answer ========
    # Find the tokens with the highest `start` and `end` scores.
    answer_start = torch.argmax(start_scores)
    answer_end = torch.argmax(end_scores)
    score =  torch.max(start_scores) + torch.max(end_scores)

    # Get the string versions of the input tokens.
    tokens = tokenizer.convert_ids_to_tokens(input['input_ids'][0])

    # Start with the first token.
    answer = tokens[answer_start]

    # Select the remaining answer tokens and join them with whitespace.
    for i in range(answer_start + 1, answer_end + 1):
        
        # If it's a subword token, then recombine it with the previous token.
        if tokens[i][0:2] == '##':
            answer += tokens[i][2:]
        
        # Otherwise, add a space then the token.
        else:
            answer += ' ' + tokens[i]
    return (score.detach().numpy(), answer)



def get_color(values):
    max_val = max(values)
    values = [max(i,0) for i in values]
    print(values)
    return ['rgb({}, {}, {}, {})'.format(0, 255, 0, (1 - x/max_val)* 0.25) for x in values]
      
def extract_answer(question, parsed_data):
    sentences = [] 
    current_line = ""
    current_index = []
    k = 5 
    stride = 2

    all_lines = parsed_data['lines']
    for idx, line in  enumerate(all_lines): 
        text =  line["text"].replace("\n", " ")
        temp = sent_tokenize(text)
        if len(temp) == 0: 
            continue
        if len(temp) == 1:
            current_line += text + " "
            current_index.append(idx)
        else:
            current_line += temp[0] 
            current_index.append(idx)
            sentences.append({"text": current_line, "line_index": current_index})

            for i in temp[1: -1]:
                sentences.append({"text": i, "line_index": [idx]})
            current_line = temp[-1] + " "
            current_index = [idx]

    if current_line:
        sentences.append({"text": current_line, "line_index": current_index})

    contexts = [] 
    for idx in range(0, max(len(sentences) - k, 1), stride): 
        valid_sentences = sentences[idx: idx + k]
        context = {"text" : " ".join([i["text"] for i in valid_sentences])}
        line_idx = [] 
        for i in valid_sentences: 
            line_idx.extend(i['line_index'])
        context["rects"] = [{'y0': all_lines[i]['y0'], 
                             'y1': all_lines[i]['y1'], 
                             'x0': all_lines[i]['x0'], 
                             'x1': all_lines[i]['x1'], 
                             'top': all_lines[i]['top']} for i in line_idx]
        contexts.append(context)
    
    best_answer = [] 
    for context in contexts:
        answer =  answer_question(question, context["text"])
        context["score"] = float(answer[0])
        context["answer_text"] = answer[1]
    
    colors = get_color([i['score'] for i in contexts])
    for idx in range(len(contexts)): 
        contexts[idx]['color'] = colors[idx]

    return contexts


def search_classifier(question, responses):
    pairs = [(question, response) for response in responses]
    input = custom_tokenizer(pairs, return_tensors='pt', padding=True, truncation=True)

    # Report how long the input sequence is.

    scores = custom(**input)[0] # The segment IDs to differentiate question from answer_text
    print(scores.shape)
    # ======== Reconstruct Answer ========
    # Find the tokens with the highest `start` and `end` scores.
    # scores = torch.max(scores, dim=-1)[0]
    return scores[:, 1].detach().numpy()

# if __name__ == '__main__': 
    from core.es import search_sections
    query = "how many number of privilege leaves employee get"
    results = search_sections(query=query, params={"project_id": "f6da25c7-8275-4b2c-bbab-cc4f8ec5e029"})
    responses = [i['_source']['text'] for i in results]
    scores = search_classifier(query, responses)
    for idx, response in enumerate(responses): 
        print(response)
        print(scores[idx])