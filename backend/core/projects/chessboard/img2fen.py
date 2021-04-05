import pickle 
import cv2
import os 
import time 
import numpy as np
import random
import chess 
import chess.svg
import cairosvg
import requests
from collections import defaultdict
from os import walk

import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, imshow, axis
from matplotlib.image import imread
from tensorflow.keras.models import load_model
from core.projects.chessboard.serving import run_small_classification



label_map = {0: ' ', 1: 'p', 2: 'n', 3: 'B', 4:'R', 5: 'Q', 6: 'k', 7: 'K', 8: 'q', 9: 'P', 10: 'N', 11: 'r', 12: 'b'}
_UNIQUE_CLASSES = [ 6, 7,]

def _save_board(fen, output_file='board_pred.png'):
    """
        Convert the board into SVG file and save locally
    """
    board = chess.Board(fen)
    board_svg = chess.svg.board(board)
    cairosvg.svg2png(bytestring=board_svg, \
        write_to=output_file)


def _show_prediction_n_input(img, fen):
    """
        Show the predicted board side by side with input image 
    """
    fig = plt.figure(figsize=(8, 8))
    img = cv2.imread(img)
    fig.add_subplot(1, 2, 1)
    plt.imshow(img)
    _save_board(fen)
    fig.add_subplot(1, 2, 2)
    img = cv2.imread(os.path.join("board_pred.png"))
    plt.imshow(img)
    plt.show()
    
   

def _pad_image(image, label): 
    color = (255,0,0)
    label = str(round(label, 2))
    image = cv2.copyMakeBorder(image ,10,10,10,10,cv2.BORDER_CONSTANT,value=color)
    cv2.putText(image, "Sco:{}".format(label), (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 1)
    return image 


def concat_tile(images, labels):    
    image_tiles = [] 
    for idx in range(8): 
        image_tiles.append([_pad_image(i, labels[8*idx + idy]) for idy, i in enumerate(images[8*idx: 8*idx + 8])])
    return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in image_tiles])


def _read_and_split_image(img, array=False):
    nRows = 8
    mCols = 8

    if not array:
        img = cv2.imread(img)

    img = cv2.resize(img, (400, 400)) 

    # Dimensions of the image
    sizeX = img.shape[1]
    sizeY = img.shape[0]

    block_map = []
    for i in range(0,nRows):
        temp = [] 
        for j in range(0, mCols):
            roi = img[int(i*sizeY/nRows):int(i*sizeY/nRows + sizeY/nRows) ,int(j*sizeX/mCols):int(j*sizeX/mCols + sizeX/mCols), :]
            temp.append(roi)
        block_map.append(temp)

    return block_map


def _load_model(model_path="./data/mobilenet_classifier.h5"):
    return load_model(model_path)

def _filter_out_duplicate_pieces(predictions, scores):
    predictions = np.array(predictions)
    scores = np.array(scores)

    for item in _UNIQUE_CLASSES:
       mask = predictions != item
       score_ = np.ma.masked_array(scores, mask=mask)
    #    print(score_)
       max_score = score_.max()
    #    print(max_score)
       indices = np.ma.where(score_!=max_score)
    #    print(indices)
       predictions[indices] = 0
    return predictions 

def _check_for_castling(grid_labels, orientation="w"):
    """[summary]

    Args:
        grid_labels ([type]): Matrix with predictions 
        orientation (str, optional): Bottom half color 
    """
    white_idx, black_idx = (-1, 0) if orientation == "w" else (0, -1)
    if orientation == "w":
        white_row = [label_map[j] for j in grid_labels[white_idx].tolist()]
        black_row = [label_map[j] for j in grid_labels[black_idx].tolist()]
    else:
        white_row = list(reversed([label_map[j] for j in grid_labels[white_idx].tolist()]))
        black_row = list(reversed([label_map[j] for j in grid_labels[black_idx].tolist()]))
    
    castling_str = ''

    if white_row[4] == 'K':
        if white_row[-1] == 'R' : 
            castling_str += 'K'
        if white_row[0] == 'R': 
            castling_str += 'Q'
    if black_row[4] == 'k':
        if black_row[0] == 'r': 
            castling_str += 'q'
        if black_row[-1] == 'r' : 
            castling_str += 'k'

    if not castling_str:
        castling_str = '-'
    return castling_str
    
    

def image2fen(img): 
    """
        Classify detected board blocks

        params:
            - img: Image array, expected shape (N, N, 3) i.e. square 
                image 
        
        returns: [img, concatenated, fen]
            - img: Detected board converted from fen 
            - concatenated: Concatenated blocks with score 
            - fen: Fen string 

    """
    grid_images = _read_and_split_image(img, array=True)
    grid_labels = []
    grid_images = np.array(grid_images) 
    new_shape = [-1] + list(grid_images.shape[2:])
    grid_images = np.reshape(grid_images, new_shape)
    preds = run_small_classification(grid_images)
    all_images = [grid_images[i] for i in range(64)]
    temp = np.max(preds, axis=-1)
    preds = np.argmax(preds, axis=-1)
    preds = _filter_out_duplicate_pieces(preds, temp)
    temp = [j for j in temp.tolist()]
    concatenated = concat_tile(all_images, temp)

    fen = ""
    grid_labels = np.reshape(preds, (8, 8))
    grid_scores = np.reshape(temp, (8, 8))

    white_count = defaultdict(int)
    black_count = defaultdict(int)
    
    for i in range(8):
        labels = [label_map[j] for j in grid_labels[i].tolist()]
        scores = grid_scores[i]
        fen_row = '' 
        blank =0 
        # Store king and queen positions 
        king_positions = []
        for label, score in zip(labels, scores): 
            if label == ' ': 
                blank += 1 
            else: 
                if blank != 0: 
                    fen_row += str(blank)
                    blank = 0 
                fen_row += label
        if label != ' ':
            key = 'top' if i <=3 else 'bottom'
            # Now if white increate the white count 
            if label.lower() != label: 
                white_count[key] += 1
            else:
                black_count[key] += 1

        if blank != 0: 
            fen_row += str(blank)
            blank = 0 
        fen += fen_row + "/"
    

    perspective = None
    # Get perspective 
    if white_count['bottom'] >= black_count['bottom'] or\
        white_count['top'] <= black_count['top']:
        perspective = 'w'
    else:
        perspective = 'b'

    fen = fen[:-1]
    if perspective != "w": 
        # Because FEN always has to be from white's perspective 
        flip_row = lambda x: "".join(reversed(x))
        rows = fen.split("/")
        reversed_rows = [flip_row(i) for i in rows]
        print(reversed_rows)
        fen = "/".join(list(reversed(reversed_rows)))

    castling_str = _check_for_castling(grid_labels, perspective)

    fen = fen + " " + perspective + " " + castling_str + " - 0 1"
    end = time.time()
    _save_board(fen)
    img = cv2.imread(os.path.join("board_pred.png"))
    return img, concatenated, fen

def main() : 
    _, _, board_images = next(walk("./tests/final/"))
    board_images = [i for i in board_images if ".png" in i]
    img = random.choice(board_images)
    img = os.path.join("./tests/final/", img)
 
    for _ in range(20):
        start = time.time()
        img = random.choice(board_images)
        img = os.path.join("./tests/final/", img)
        image = cv2.imread(img)
        image2fen(img=image)
        end = time.time()
        print("Time taken {}".format(end- start))

if __name__ == '__main__':
    main()