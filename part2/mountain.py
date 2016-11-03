#!/usr/bin/python
#
# Mountain ridge finder
# Based on skeleton code by D. Crandall, Oct 2016
#

from PIL import Image
import numpy as np
from numpy import *
from scipy.ndimage import filters
from scipy.misc import imsave
import sys

# calculate "Edge strength map" of an image
#
def edge_strength(input_image):
    grayscale = array(input_image.convert('L'))
    filtered_y = zeros(grayscale.shape)
    filters.sobel(grayscale,0,filtered_y)
    return filtered_y**2

# draw a "line" on an image (actually just plot the given y-coordinates
#  for each x-coordinate)
# - image is the image to draw on
# - y_coordinates is a list, containing the y-coordinates and length equal to the x dimension size
#   of the image
# - color is a (red, green, blue) color triple (e.g. (255, 0, 0) would be pure red
# - thickness is thickness of line in pixels
#
def draw_edge(image, y_coordinates, color, thickness):
    for (x, y) in enumerate(y_coordinates):
        for t in range( max(y-thickness/2, 0), min(y+thickness/2, image.size[1]-1 ) ):
            image.putpixel((x, t), color)
    return image

#This method finds the coordinates of the ridge line
# Formula implemented: p(s/w) = P(w/s) * P(s) / P(w)

def findRedLine(edge_strength):
    ridge = []

    rowLst = []
    for row in edge_strength:
        rowLst.append(sum(row))
    colLst = []
    for j in range(len(edge_strength[0])):
        colLst.append(sum([edge_strength[i][j] for i in range(len(edge_strength))]))

    lst = []
    for j in range(len(edge_strength[0])):
        for i in range(len(edge_strength)):
            lst.append((edge_strength[i][j] / colLst[j]) * (edge_strength[i][j] /  rowLst[i]))
        ridge.append(lst.index(max(lst)))
        lst = []

    return ridge


# main program
#
#(input_filename, output_filename, gt_row, gt_col) = sys.argv[1:]
input_filename="mountain9.jpg"
output_filename="output.jpg"
gt_row,gt_col=0,0
# load in image 
input_image = Image.open(input_filename)

# compute edge strength mask
edge_strength = edge_strength(input_image)
imsave('edges.jpg', edge_strength)


# You'll need to add code here to figure out the results! For now,
# just create a horizontal centered line.

vitterMap = []
#Create a matrix with same number of values as edge_strength but all values set to 0



ridge = findRedLine(edge_strength)

# output answer
imsave(output_filename, draw_edge(input_image, ridge, (255, 0, 0), 5))
