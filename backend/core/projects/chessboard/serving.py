import pickle
import numpy as np
import time
import requests
import subprocess
import re
import os 
import cv2
import grpc
import numpy as np
from PIL import Image

import tensorflow as tf
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

if os.environ["ENV"] != "local":
    host = 'tf-serving'
    grpc_port = '8500'
    rest_port = '8501'
else:
    print("local")
    host = 'localhost'
    grpc_port = '8511'
    rest_port = '8510'


SMALL_CLASSIFICATION = 'en_classification'
EN_CLASSIFICATION = 'en_classification'

CLASSIFICATION = 'classification'
SEGMENTATION = 'mv2_segmentation'
# SEGMENTATION = 'segmentation'

signature_name = 'serving_default'
CONFIG = {
    # SMALL_CLASSIFICATION: {'input_name': 'input_1', 'output_name': 'dense_1'},
    # SEGMENTATION: {'input_name': 'in', 'output_name': 'out'},
    SEGMENTATION: {'input_name': 'in', 'output_name': 'out', "version": 1},
    # CLASSIFICATION: {'input_name': 'input_1', 'output_name': 'dense_1'},
    EN_CLASSIFICATION: {'input_name': 'input_4', 'output_name': 'dense_7'},
}
# channel = implementations.insecure_channel(host, int(grpc_port))
channel = grpc.insecure_channel("{}:{}".format(host, int(grpc_port)))
# stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)


def prepare_grpc_request(model_name, input_name, signature_name, data, version=1):
    request = predict_pb2.PredictRequest()
    request.model_spec.name = model_name
    # request.model_spec.version.value = version
    request.model_spec.signature_name = signature_name
    request.inputs[input_name].CopyFrom(
        tf.make_tensor_proto(data, shape=data.shape, dtype=None))
    return request


def run_segmentation(image, size=513):
    width, height = image.size
    resize_ratio = 1.0 * size / max(width, height)
    target_size = (int(resize_ratio * width), int(resize_ratio * height))
    resized_image = image.convert('RGB').resize(target_size, Image.ANTIALIAS)
    images = np.array([np.asarray(resized_image)])
    version = CONFIG[SEGMENTATION].get('version', 1)
    request = prepare_grpc_request(SEGMENTATION, CONFIG[SEGMENTATION]['input_name'], \
        signature_name, images, version=version)
    pred = stub.Predict(request, timeout=600)
    output_name = CONFIG[SEGMENTATION]['output_name']
    seg_map = tf.make_ndarray(pred.outputs[output_name])[0]
    resized_im = np.asarray(resized_image)
    redImg = np.zeros(resized_im.shape, resized_im.dtype)
    redImg[:,:] = (0, 0, 255)
    redMask = cv2.bitwise_and(redImg, redImg, mask=seg_map.astype(np.uint8))
    dst = cv2.addWeighted(redMask, 1, resized_im, 1, 0, resized_im)
    return dst, seg_map 

def run_small_classification(images):
    images = images.astype(np.float32)
    input_name = CONFIG[EN_CLASSIFICATION]['input_name']
    output_name = CONFIG[EN_CLASSIFICATION]['output_name']
    version = CONFIG[EN_CLASSIFICATION].get('version', 1)

    request = prepare_grpc_request(EN_CLASSIFICATION, input_name, signature_name,\
                images, version=version)
    pred = stub.Predict(request, timeout=600)
    output_name = CONFIG[EN_CLASSIFICATION]['output_name']
    pred = tf.make_ndarray(pred.outputs[output_name])
    return pred 