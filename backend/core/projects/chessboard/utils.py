import cv2
import numpy as np
from scipy.spatial import distance as dist
from operator import itemgetter
from glob import glob
import matplotlib.pyplot as plt

def order_points(pts):
	# sort the points based on their x-coordinates
	xSorted = pts[np.argsort(pts[:, 0]), :]
	# grab the left-most and right-most points from the sorted
	# x-roodinate points
	leftMost = xSorted[:2, :]
	rightMost = xSorted[2:, :]
	# now, sort the left-most coordinates according to their
	# y-coordinates so we can grab the top-left and bottom-left
	# points, respectively
	leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
	(tl, bl) = leftMost
	# now that we have the top-left coordinate, use it as an
	# anchor to calculate the Euclidean distance between the
	# top-left and right-most points; by the Pythagorean
	# theorem, the point with the largest distance will be
	# our bottom-right point
	D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
	(br, tr) = rightMost[np.argsort(D)[::-1], :]
	# return the coordinates in top-left, top-right,
	# bottom-right, and bottom-left order
	return np.array([tl, tr, br, bl], dtype=np.float32)

def correct_perspective(img, box):
	# Coordinates that you want to Perspective Transform
	# Size of the Transformed Image
	box = order_points(np.float32(box))
	pts2 = np.float32([[0,0], [600,0], [600,600], [0,600]])
	# M = cv2.getPerspectiveTransform(box, pts2)
	M, _ = cv2.findHomography( box, pts2, cv2.RANSAC, 5.0)
	# dst = cv2.perspectiveTransform(np.array([keypoints], dtype=np.float32), M)
	dst = cv2.warpPerspective(img, M, (600, 600), flags=cv2.INTER_LINEAR)

	return dst

def segment_board(img, mask):
	# If mask is not of same size then resize
	mask = mask.astype(np.uint8)
	if img.shape[:2] != mask.shape[:2]:
		height, width = img.shape[:2]
		mask = cv2.resize(mask, (width, height)) 
	contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	if len(contours) > 0: 
		valid_contour = max([(contour, cv2.contourArea(contour)) for contour in contours], key=lambda x: x[1])[0]
		# rect = cv2.minAreaRect(valid_contour)
		# box = cv2.boxPoints(rect)
		# box = np.int0(box)
		epsilon = 0.01*cv2.arcLength(valid_contour,True)
		approx = cv2.approxPolyDP(valid_contour,epsilon,True)
		if approx.shape[0] == 4:
			approx = np.squeeze(approx, axis=1)
			box = approx
		else:
			rect = cv2.minAreaRect(valid_contour)
			box = cv2.boxPoints(rect)
			box = np.int0(box)
		transformed_seg = correct_perspective(img, box)
		return transformed_seg
	else:
		return None 

def plot_box(img, mask):
	mask = mask.astype(np.uint8)
	if img.shape[:2] != mask.shape[:2]:
		height, width = img.shape[:2]
		mask = cv2.resize(mask, (width, height)) 
	contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	if len(contours) > 0:
		valid_contour = max([(contour, cv2.contourArea(contour)) for contour in contours], key=lambda x: x[1])[0]
		rect = cv2.minAreaRect(valid_contour)
		box = cv2.boxPoints(rect)
		# Blue color in BGR 
		color = (255, 255, 0) 
		pts = order_points(np.float32(box))
		pts = pts.reshape((-1, 1, 2)) 
		thickness = 2
		isClosed=True
		box = cv2.boxPoints(rect) # cv2.boxPoints(rect) for OpenCV 3.x
		box = np.int0(box)
		epsilon = 0.01*cv2.arcLength(valid_contour,True)
		approx = cv2.approxPolyDP(valid_contour,epsilon,True)

		cv2.drawContours(img, [approx], 0, (255,255,255), 3)
		rect = cv2.minAreaRect(approx)
		# Creates box around that rectangle
		# box = cv2.boxPoints(rect)

		# rect = cv2.minAreaRect(approx)
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		# print(approx)
		cv2.drawContours(img, [box], 0, (255,255,), 3)


		# cv2.drawContours(img,[box],0,(0,0,255),2)
		# img = cv2.polylines(img, np.int32([pts]),  
		# 					isClosed, color, thickness)
		# cv2.drawContours(img, valid_contour, -1, (0, 255, 0), 3)

		return img
	else: 
		return None