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
magic_mcmc_no = 10000
# This function gets the best point for starting the mcmc
def get_init_point(ridge):
    min = 99999; # some high val
    
    for i in range(len(ridge)-1):
        if(ridge[i] < min ):
            min = ridge[i]
            index = i
    return (index,min) #(x,y)

# MCMC Transistion Probablitiy
# Not perfect
def transition_Prob(x1,x2):
    # smooth = 2
    smooth = 2.8
    x1 = 1 if x1==0 else x1
    x2 = 1 if x2==0 else x2
    if (x1 < x2):
        return math.pow(x1/(x2 * 1.0),smooth)
    else:
        return math.pow(x2/(x1 * 1.0),smooth)

# Emission probability
# Given 0.1 prob if the strenght is zero so as to avoid complete eliminate of samples
def emmission_Prob(strength,max_val):
    val = (strength/ max_val)
    smooth = 0.008 # have to make it dynamic - based on average - 0.005
    if(val <= smooth):
        return smooth
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

def average_sample(sample):
    colLst = []
    for j in range(len(sample[0])):
        colLst.append(sum([sample[i][j] for i in range(len(sample))])/magic_mcmc_no) #col
    return colLst

def plot_blue_line(edge_strength,ridge):
    print "plot_blue_line"
    init_point = get_init_point(ridge)
    print init_point
    sample = []
    sample.append(ridge)
    x = init_point[0] -1
    y = init_point[1]
    # x = 45
    # y = 160
    sampleItr = 0
    toggle = True
    print ridge
    colLst = []
    for j in range(len(edge_strength[0])):
        colLst.append(sum([edge_strength[i][j] for i in range(len(edge_strength))]))
    # print colLst
    for itr in range(magic_mcmc_no):
        if(toggle):
            x += 1
        else:
            x -=1
        temp = list(sample[sampleItr])
        lst = []

        for i in range(len(edge_strength)): #col = height 
            em = emmission_Prob(edge_strength[i][x],colLst[x])  
            # print (edge_strength[i][x],em)
            # em = 1
            # h = ^3.5
            h = pow((((len(edge_strength)-i)*0.9)/(len(edge_strength)*1.0)),3.8)
            tr = transition_Prob(y,i)
            if((x+1) == len(ridge) - 1  or (x+1) == 0):
                trf = pow(transition_Prob(temp[x+1],i),2)
            else: 
                trf = 1
            # trf = 1
            # print tr
            lst.append(em*h*tr*trf)
        # print "Before:: "+ str(y)
        y = lst.index(max(lst))
        # print "Now:: "+ str(y)
        temp[x] = y
        # print temp
        sample.append(temp);
        sampleItr +=1;        
        if(x == len(ridge) - 1  or x == 0):
            toggle = not toggle
    return sample


# main program - python mountain.py mountain.jpg new_output_file.jpg 0 0
#(input_filename, output_filename, gt_row, gt_col) = sys.argv[1:]
# file = "2";
file = sys.argv[1]
# print file
# quit()
input_filename="mountain"+file+".jpg"
output_filename="output"+file+".jpg"
gt_row,gt_col=0,0

# load in image 
input_image = Image.open(input_filename)
# compute edge strength mask
edge_strength = edge_strength(input_image)
imsave('edges.jpg', edge_strength)

ridge = findRedLine(edge_strength)

# New function Added
sample = plot_blue_line(edge_strength,ridge);

# imsave("Test.jpg", draw_edge(input_image,[169,150] , (0, 0, 255), 5))
# print ridge
# output answer
# imsave(output_filename, draw_edge(input_image, ridge, (255, 0, 0), 5))

# imsave(output_filename, draw_edge(input_image, sample[len(sample) - 1], (255, 0, 0), 5))
imsave(output_filename, draw_edge(input_image, average_sample(sample), (255, 0, 0), 5))
