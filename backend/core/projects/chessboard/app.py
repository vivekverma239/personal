import os 
import cv2
import random 
import pandas as pd
import numpy as np

from PIL import Image
from .utils import segment_board, plot_box
import time 
from .img2fen import image2fen
from .serving import run_segmentation


def recognize_board(img_file=None):
    base_name = None
    res = {}
    if img_file is not None:
        image = Image.open(img_file).convert('RGB')
        save_file_org = img_file
        base_name = ".".join(save_file_org.split(".")[:-1])
    else:
        board_images = os.listdir("./media/tests/")
        board_images = [i for i in board_images if all(j not in i for j  in ["blend", "board", "predicted"])]

        board_images = [i for i in board_images \
                        if ".png" in i \
                        or ".jpg" in i \
                        or ".jpeg" in i]
        demo_image = random.choice(board_images)
        demo_image = os.path.join("./media/tests/", demo_image)
        image = Image.open(demo_image).convert('RGB')
        save_file_org = demo_image
        base_name = ".".join(save_file_org.split(".")[:-1])

    res["image"] = save_file_org

    start = time.time()
    blended_img, pred_mask = run_segmentation(image)
    end = time.time()
    blended_img = plot_box(blended_img, pred_mask)
    if blended_img is not None:
        cv2.imwrite("{}-blend.jpg".format(base_name), blended_img)
        res["blend"] = "{}-blend.jpg".format(base_name)


    start = time.time()
    board = segment_board(np.array(image), pred_mask)
    fen = ""
    if board is not None:
        cv2.imwrite("{}-board.jpg".format(base_name), board)
        res["board"] = "{}-board.jpg".format(base_name)
        predicted_board, concated, fen = image2fen(board)
        cv2.imwrite("{}-predicted.jpg".format(base_name), predicted_board)
        res["predicted"] = "{}-predicted.jpg".format(base_name)
        res["success"] = True
        res["fen"] = fen
        end = time.time()

    return res