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
def transition_Prob(sx1,sx2,es1=0,es2=0):
    smooth = 2.8
    smooth_prop = 1.0
    if sx1==0 or sx2 ==0:
        sx1+=1
        sx2 += 1
    proportional = 1.0
    # if(es1 == 0 or es2 ==0):
    #     return 0.00001
    # if (es1 < es2):
    #     proportional = (math.pow(es1/(es2 * 1.0),smooth_prop )) *1000
    # else:
    #     proportional =  (math.pow(es2/(es1 * 1.0),smooth_prop )) * 1000

    if (sx1 < sx2):
        return math.pow(sx1/(sx2 * 1.0),smooth)
    else:
        return math.pow(sx2/(sx1 * 1.0),smooth)

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
        colLst.append(sum([sample[i][j] for i in range(len(sample))])/len(sample)) #col
    return colLst

def plot_blue_line(edge_strength,ridge):
    print "plot_blue_line"
    init_point = get_init_point(ridge)
    #print init_point
    sample = []
    sample.append(ridge)
    x = init_point[0] - 1  # index of the sx value in ridge
    y = init_point[1] # actual sx value
    # x = 45
    # y = 160
    sampleItr = 0
    toggle = True
    #print ridge
    colLst = []
    for j in range(len(edge_strength[0])):
        colLst.append(sum([edge_strength[i][j] for i in range(len(edge_strength))]))
    # print colLst
    for itr in range(magic_mcmc_no):
        if(toggle):
            x += 1
            #tx = x -1
        else:
            x -=1
            #tx = x +1
        temp = list(sample[sampleItr])
        lst = []

        for i in range(len(edge_strength)): #col = height 
            em = emmission_Prob(edge_strength[i][x],colLst[x])  
            # print (edge_strength[i][x],em)
            # em = 1
            # h = ^3.5
            h = pow((((len(edge_strength)-i)*0.9)/(len(edge_strength)*1.0)), 4.6)
            #tr = transition_Prob(y,i,edge_strength[y][tx],edge_strength[i][x])
            tr = transition_Prob(y, i)
            if((x+1) == len(ridge) - 1  or (x+1) == 0):
                trf = pow(transition_Prob(temp[x+1],i),2)
            else:
                trf = 1
            #trf = 1
            # print tr
            lst.append(em*h*tr*trf)

            #break
        #break
        # print "Before:: "+ str(y)
        y = lst.index(max(lst))
        # print "Now:: "+ str(y)
        temp[x] = y
        # print temp
        sample.append(temp);
        sampleItr +=1;        
        if(x == len(ridge) - 1  or x == 0):
            toggle = not toggle
            #sample.append(temp);
    return sample

def plot_green_line(edge_strength, ridge,gt_row,gt_col):
    print "plot_green_line"

    # print init_point
    sample = []
    sample.append(ridge)
    x = gt_row  # index of the sx value in ridge  282
    y = gt_col  # actual sx value 32
    # x = 45
    # y = 160
    sampleItr = 0
    toggle = True
    # print ridge
    colLst = []
    for j in range(len(edge_strength[0])):
        colLst.append(sum([edge_strength[i][j] for i in range(len(edge_strength))]))
    # print colLst
    for itr in range(magic_mcmc_no):
        if (toggle):
            x += 1
            # tx = x -1
        else:
            x -= 1
            # tx = x +1
        temp = list(sample[sampleItr])
        lst = []

        for i in range(len(edge_strength)):  # col = height

            em = emmission_Prob(edge_strength[i][x], colLst[x])
            # print (edge_strength[i][x],em)
            # em = 1
            # h = ^3.5
            h = pow((((len(edge_strength) - i) * 0.9) / (len(edge_strength) * 1.0)), 4.6)
            # tr = transition_Prob(y,i,edge_strength[y][tx],edge_strength[i][x])
            tr = transition_Prob(y, i)
            if ((x + 1) == len(ridge) - 1 or (x + 1) == 0):
                trf = pow(transition_Prob(temp[x + 1], i), 2)
            else:
                trf = 1
            # trf = 1
            # print tr
            lst.append(em * h * tr * trf)

            # break
        # break
        # print "Before:: "+ str(y)
        y = lst.index(max(lst))
        # print "Now:: "+ str(y)
        temp[x] = y
        # print temp
        sample.append(temp);
        sampleItr += 1;
        if (x == len(ridge) - 1 or x == 0):
            toggle = not toggle
            # sample.append(temp);
    return sample


# main program - python mountain.py mountain.jpg new_output_file.jpg 0 0
#(input_filename, output_filename, gt_row, gt_col) = sys.argv[1:]
file = '1'

while True:
    if file=='10':
        break
    input_filename="mountain"+file+".jpg"
    output_filename="output"+file+".jpg"
    gt_row,gt_col=49,50
    print input_filename
    # load in image
    input_image = Image.open(input_filename)
    # compute edge strength mask
    edge_strength_value = edge_strength(input_image)
    imsave('edges.jpg', edge_strength_value)

    ridge = findRedLine(edge_strength_value)
    imsave(output_filename, draw_edge(input_image, ridge, (255, 0, 0), 5))
    # New function Added
    sample = plot_blue_line(edge_strength_value,ridge);
    imsave(output_filename, draw_edge(input_image, sample[-1], (0, 0, 255), 5))

    sample = plot_green_line(edge_strength_value, ridge,gt_row,gt_col);
    imsave(output_filename, draw_edge(input_image, sample[-1], (0, 255, 0), 5))

    # imsave("Test.jpg", draw_edge(input_image,[169,150] , (0, 0, 255), 5))
    # print ridge
    # output answer
    # imsave(output_filename, draw_edge(input_image, ridge, (255, 0, 0), 5))

    # imsave(output_filename, draw_edge(input_image, sample[len(sample) - 1], (255, 0, 0), 5))
    #imsave(output_filename, draw_edge(input_image, average_sample(sample), (255, 0, 0), 5))

    file = str(int(file) + 1)
