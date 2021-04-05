import tensorflow_hub as hub
import numpy as np
import tensorflow as tf 

host = "localhost"
port = "8510"

# module = hub.load('https://tfhub.dev/google/universal-sentence-encoder-qa/3')
# embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")

# def encode_questions(questions):
#     question_embeddings = module.signatures['question_encoder'](
#                 tf.constant(questions))
#     return question_embeddings['outputs'].numpy()

# def encode_responses(responses):
#     response_embeddings = module.signatures['response_encoder'](
#             input=tf.constant(responses),
#             context=tf.constant(responses))
#     return response_embeddings['outputs'].numpy()

# def encode_use(sentences):
#     return embed(sentences).numpy()

def encode_questions(questions):
    """Runs inference on a single image.

    Args:
      image: A PIL.Image object, raw input image.

    Returns:
      resized_image: RGB image resized from original input image.
      seg_map: Segmentation map of `resized_image`.
    """
    data = {"instances": questions}
    url = "http://{}:{}/v1/models/use_qa:question_encoder".format(host, rest_port)
    response = requests.post(url, json=data)
    if 'predictions' not in response.json(): 
        print(response.json())
    predictions = np.array(response.json()['predictions'])
    return  predictions

def encode_responses(responses):
    """Runs inference on a single image.

    Args:
      image: A PIL.Image object, raw input image.

    Returns:
      resized_image: RGB image resized from original input image.
      seg_map: Segmentation map of `resized_image`.
    """
    data = {"instances": responses}
    url = "http://{}:{}/v1/models/use_qa:response_encoder".format(host, rest_port)
    response = requests.post(url, json=data)
    if 'predictions' not in response.json(): 
        print(response.json())
    predictions = np.array(response.json()['predictions'])
    return  predictions