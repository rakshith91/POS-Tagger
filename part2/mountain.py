#!/usr/bin/python
#
# Mountain ridge finder
# Based on skeleton code by D. Crandall, Oct 2016
#
# from __future__ import division
from PIL import Image
import numpy as np
from numpy import *
from scipy.ndimage import filters
from scipy.misc import imsave
import sys

max_str = 255**2
magic_mcmc_no = 5000
# This function gets the best point for starting the mcmc
def get_init_point(ridge):
    #@todo : This function could be replaced with return (ridge.index(min(ridge)) , min(ridge))
    # This change doesnt affect functionality
    min = 99999; # some high val
    for i in range(len(ridge)-1):
        if(ridge[i] < min ):
            min = ridge[i]
            index = i
    return (index,min) #(x,y)

def transition_Prob(x1,x2):
    if (x1 < x2):
        return x1/(x2 * 0.9)
    else:
        return x2/(x1 * 0.9)

def emmission_Prob(strength):
    val = (strength/ max_str)
    if(strength == 0):
        return 0.1 #@todo(idea) : I think 0.1 is  a very big number as most of times val would be a fraction between 0 and 1
    else:
        return val
# calculate "Edge strength map" of an image
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
    data = {}
    for j in range(len(edge_strength[0])): #row
    # for j in range(50):
        lst = []
        for i in range(len(edge_strength)): #col
            lh = (edge_strength[i][j] / max_str)
            h = (((len(edge_strength)-i)*0.9)/(len(edge_strength)*1.0))
            lst.append(lh*h)
        ridge.append(lst.index(max(lst)))
    return ridge

def plot_blue_line(edge_strength,ridge):
    print "plot_blue_line"
    init_point = get_init_point(ridge)
    print init_point
    sample = []
    sample.append(ridge)
    x = init_point[0] + 1
    y = init_point[1]
    sampleItr = 0
    toggle = True
    print ridge
    for itr in range(magic_mcmc_no):
        #@todo : what is the below line doing
        temp = list(sample[sampleItr])
        lst = []
        for i in range(len(edge_strength)): #col = height 
            em = emmission_Prob(edge_strength[i][x])  
            # em = (edge_strength[i][x] / max_str)*0.5
            # em = 1
            h = (((len(edge_strength)-i)*0.9)/(len(edge_strength)*1.0))
            #@todo : check if in the other direction if you are considering the point behind you
            tr = transition_Prob(y,i) * 0.9
            # print tr
            lst.append(em*h*tr)
        y = lst.index(max(lst))
        temp[x] = y
        print temp
        sample.append(temp);
        sampleItr +=1;
        if(toggle):
            x += 1
        else:
            x -=1
        if(x == len(ridge) -1  or x == 0):
            toggle = not toggle
    return sample
    
def findAvg(sample):
    avgSample=[]
    for i in range(len(sample[0])):
        x=0
        for j in range(len(sample)):
            x+=sample[j][i]
        avgSample.append(x/len(sample))

    return avgSample

# main program - python mountain.py mountain.jpg new_output_file.jpg 0 0
#(input_filename, output_filename, gt_row, gt_col) = sys.argv[1:]
input_filename="mountain7.jpg"
output_filename="output.jpg"
gt_row,gt_col=0,0

# load in image 
input_image = Image.open(input_filename)
# compute edge strength mask
edge_strength = edge_strength(input_image)
imsave('edges.jpg', edge_strength)

ridge = findRedLine(edge_strength)

sample = plot_blue_line(edge_strength,ridge);
avgSample = findAvg(sample)
# imsave("Test.jpg", draw_edge(input_image,[169,150] , (0, 0, 255), 5))
# print ridge
# output answer
# imsave(output_filename, draw_edge(input_image, ridge, (255, 0, 0), 5))
imsave(output_filename, draw_edge(input_image, sample[len(sample) - 1], (0, 0, 255), 5))

#@todo: The below is red line is drawn using the average sample 
imsave(output_filename, draw_edge(input_image, avgSample, (255, 0, 0), 5))

