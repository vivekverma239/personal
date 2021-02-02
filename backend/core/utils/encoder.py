import tensorflow_hub as hub
import numpy as np
import tensorflow as tf 


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