import os
from os import walk
from io import BytesIO
import tarfile
import time 
import cv2
import random 
import requests
import tempfile
from six.moves import urllib

from matplotlib import gridspec
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
from serving import run_segmentation
# from serving_grpc import run_segmentation
# from serving_openvino import run_segmentation


import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

class DeepLabModel(object):
  """Class to load deeplab model and run inference."""

  INPUT_TENSOR_NAME = 'ImageTensor:0'
  OUTPUT_TENSOR_NAME = 'SemanticPredictions:0'
  INPUT_SIZE = 513
  FROZEN_GRAPH_NAME = 'frozen_inference_graph'

  def __init__(self, graph_file="exported"):
    """Creates and loads pretrained deeplab model."""
    self.graph = tf.Graph()

    graph_def = None

    # file_handle = open("data/finetuned_mobilenet/exported_graph.pb", "rb")
    file_handle = open("data/xception_seg_model/exported_graph.pb", "rb")

    graph_def = tf.GraphDef.FromString(file_handle.read())


    with self.graph.as_default():
      tf.import_graph_def(graph_def, name='')

    self.sess = tf.Session(graph=self.graph)

  def run(self, image):
    """Runs inference on a single image.

    Args:
      image: A PIL.Image object, raw input image.

    Returns:
      resized_image: RGB image resized from original input image.
      seg_map: Segmentation map of `resized_image`.
    """
    width, height = image.size
    resize_ratio = 1.0 * self.INPUT_SIZE / max(width, height)
    target_size = (int(resize_ratio * width), int(resize_ratio * height))
    resized_image = image.convert('RGB').resize(target_size, Image.ANTIALIAS)
    batch_seg_map = self.sess.run(
        self.OUTPUT_TENSOR_NAME,
        feed_dict={self.INPUT_TENSOR_NAME: [np.asarray(resized_image)]})
    seg_map = batch_seg_map[0]
    return resized_image, seg_map




def create_pascal_label_colormap():
  """Creates a label colormap used in PASCAL VOC segmentation benchmark.

  Returns:
    A Colormap for visualizing segmentation results.
  """
  colormap = np.zeros((256, 3), dtype=int)
  ind = np.arange(256, dtype=int)

  for shift in reversed(range(8)):
    for channel in range(3):
      colormap[:, channel] |= ((ind >> channel) & 1) << shift
    ind >>= 3

  return colormap


def label_to_color_image(label):
  """Adds color defined by the dataset colormap to the label.

  Args:
    label: A 2D array with integer type, storing the segmentation label.

  Returns:
    result: A 2D array with floating type. The element of the array
      is the color indexed by the corresponding element in the input label
      to the PASCAL color map.

  Raises:
    ValueError: If label is not of rank 2 or its value is larger than color
      map maximum entry.
  """
  if label.ndim != 2:
    raise ValueError('Expect 2-D input label')

  colormap = create_pascal_label_colormap()

  if np.max(label) >= len(colormap):
    raise ValueError('label value too large.')

  return colormap[label]


def vis_segmentation(image, seg_map):
  """Visualizes input image, segmentation map and overlay view."""
  plt.figure(figsize=(15, 5))
  grid_spec = gridspec.GridSpec(1, 4, width_ratios=[6, 6, 6, 1])

  plt.subplot(grid_spec[0])
  plt.imshow(image)
  plt.axis('off')
  plt.title('input image')

  plt.subplot(grid_spec[1])
  seg_image = label_to_color_image(seg_map).astype(np.uint8)
  plt.imshow(seg_image)
  plt.axis('off')
  plt.title('segmentation map')

  plt.subplot(grid_spec[2])
  plt.imshow(image)
  plt.imshow(seg_image, alpha=0.7)
  plt.axis('off')
  plt.title('segmentation overlay')

  unique_labels = np.unique(seg_map)
  ax = plt.subplot(grid_spec[3])
  plt.imshow(
      FULL_COLOR_MAP[unique_labels].astype(np.uint8), interpolation='nearest')
  ax.yaxis.tick_right()
  plt.yticks(range(len(unique_labels)), LABEL_NAMES[unique_labels])
  plt.xticks([], [])
  ax.tick_params(width=0.0)
  plt.grid('off')
  plt.show()


LABEL_NAMES = np.asarray([
    'background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus',
    'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike',
    'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tv'
])

FULL_LABEL_MAP = np.arange(len(LABEL_NAMES)).reshape(len(LABEL_NAMES), 1)
FULL_COLOR_MAP = label_to_color_image(FULL_LABEL_MAP)

# MODEL = DeepLabModel()

def process_image(image):
    resized_im, seg_map = MODEL.run(image)
    pred_mask = label_to_color_image(seg_map).astype(np.uint8)
    resized_im = np.array(resized_im)
    redImg = np.zeros(resized_im.shape, resized_im.dtype)
    redImg[:,:] = (0, 0, 255)
    redMask = cv2.bitwise_and(redImg, redImg, mask=seg_map.astype(np.uint8))
    dst = cv2.addWeighted(redMask, 1, resized_im, 1, 0, resized_im)
    return dst, seg_map


def run_visualization(file_path):
  """Inferences DeepLab model and visualizes result."""
  _, _, board_images = next(walk("./tests/"))
  for _ in range(20):
    img = random.choice(board_images)
    img = os.path.join("./tests/", img)
    file_path = img
    start = time.time()
    try:
      f = open(file_path, "rb")
      jpeg_str = f.read()
      original_im = Image.open(BytesIO(jpeg_str))
    except IOError:
      print('Cannot retrieve image. Please check url: ' + file_path)
      return

    board_images = [i for i in board_images if ".jpg" in i]
    print('running deeplab on image %s...' % file_path)
    # resized_im, seg_map = MODEL.run(original_im)
    resized_im, seg_map = run_segmentation(original_im)
    print(seg_map.shape)
    print("Time taken", time.time() - start)
    # vis_segmentation(resized_im, seg_map)

if __name__ == '__main__':
    _, _, board_images = next(walk("./tests/"))
    board_images = [i for i in board_images if ".jpg" in i]
    img = random.choice(board_images)
    img = os.path.join("./tests/", img)
    run_visualization(img)
