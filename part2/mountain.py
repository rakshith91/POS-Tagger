#!/usr/bin/python
#
# Mountain ridge finder
# Based on skeleton code by D. Crandall, Oct 2016
#
# from __future__ import division


"""
NOTE:- In some images the red,blue and green line overlap on each other and ultimately one of them is clearly visible to naked eye.
(1) Problem Formulation:
    This problem is formulated as a hidden markov model where we have few hidden variables about which we need to find out using some
    observed variables . Here the hidden variables are the row values s_x where x=[1,2,3,4,...m]. And observed values are the image
    gradient vectors w_1,w_2,....w_m.
    We need to compute P(s_i|w_i)
    Note: Denominators gets cancel as this problem deals with comparision between points on the image 
    Emission prob -  strength of point - P(w_i|s_i)
    Transition prob - closeness of the current point to the previous point - P(s_(i-1)|s_i). We also tried the proportionality of their edge 
    strength but its result were not good.
    P(s_i|s_(i-1),w_i) = P(s_(i-1)|s_i) * P(w_i|s_i) * P(s_i)
(2) How our program works:
    We have implemented three approaches:-
    1. In this approach we assume that every s_i value depends on only one w_i value i.e., it depends on the column vector it is present in.
        So, we have to find P(s_i|w_i) = P(w_i|s_i) * P(s_i) / P(w_i). This is equivalent to picking up a cell in every column which has
        maximum gradient value in that particular column.
    2. In the second approach we have used MCMC to generate samples. We have used the output ridge line from the above method as input(first sample)
        to this second approach. We have taken first sample and select the s_i value in it which corresponds to highest point of our
        current sample ridge line. Assuming that the rest of all s_x values are correct we try to find the best value for s_i.
        We do this by calculating a combination of transition and emission probabilites for every cell in that column and find the best
        value in that column. Thus we find the best value for that column and move to the next column and do the same for the column and so on.
        Once we are done with adjusting  s_x values for all the columns we consider that as our new sample. In this way we generate
        a lot of samples and at the end choose the best sample out of it, according to gibbs sampling the distribution converges 
        to the actual distribution with more samples.
    3.  In the previous section we used to start with a random initial point choosen from the first ridge line.
        But here we have some human input. So, we consider the s_i value situated in the next column as our initial point and try to
        start generating samples from there. As now we surely know a point which is on the ridge line, we give higher weights for the
        transition probabilities as we know that the next point would be close to the previous point and so on.
    Design Decisions:
    1.  We have added appropriate weights to points near the top of the image as moutain ranges are most probable to occur at the top of
        the image.
    2.  Suitable weights for emission and transition probabity has been chosen.
    3.  Found that increasing samples beyond 10000 didn't improved the ridge line.
    4.  To avoid zero probability, emision probability having very small values are provided with minimum threshold value.
3) Problems we faced:
    1. Coming up with a good combination of transition and emission probabilites was a bit of challenge. And another challenge we faced was when
    there are some other objects in the image which closely resemble a mountain range, like a chain of trees. In such cases the pixels on the
    trees were being considered into the ridge line as tree pixels have higher gradient and so higher emission probabilities. To counter this
    issue we have included a heuristic height factor which gives higher heuristic value for points which are on higher altitudes when compared
    to points on lower heights. As mountains tend to be on higher heights than trees mountain range was given more heuristic value than trees
    below it.
    2. Another challenge was to select best ridge line out of multiple samples generated. We have decided to go with the last sample as it
        was giving better results.

"""
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
def transition_Prob(sx1,sx2,smooth=2.8):
    if sx1==0 or sx2 ==0:
        sx1+=1
        sx2 += 1

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

# def average_sample(sample):
#     colLst = []
#     for j in range(len(sample[0])):
#         colLst.append(sum([sample[i][j] for i in range(len(sample))])/len(sample)) #col
#     return colLst

#This method returns the samples for drawing blue ridge line
def plot_blue_line(edge_strength,ridge):
    init_point = get_init_point(ridge)
    sample = []
    sample.append(ridge)
    x = init_point[0] - 1  # index of the sx value in ridge
    y = init_point[1] # actual sx value
    sampleItr = 0
    toggle = True
    colLst = []
    for j in range(len(edge_strength[0])):
        colLst.append(sum([edge_strength[i][j] for i in range(len(edge_strength))]))
    for itr in range(magic_mcmc_no):
        if(toggle):
            x += 1
        else:
            x -=1
        temp = list(sample[sampleItr])
        lst = []

        for i in range(len(edge_strength)): #col = height
            em = emmission_Prob(edge_strength[i][x],colLst[x])
            h = pow((((len(edge_strength)-i)*0.9)/(len(edge_strength)*1.0)), 4.6)
            tr = transition_Prob(y, i)
            if((x+1) == len(ridge) - 1  or (x+1) == 0):
                trf = pow(transition_Prob(temp[x+1],i),2)
            else:
                trf = 1
            lst.append(em*h*tr*trf)

        y = lst.index(max(lst))
        temp[x] = y
        sample.append(temp);
        sampleItr +=1;
        if(x == len(ridge) - 1  or x == 0):
            toggle = not toggle
    return sample

#This method returns the samples for drawing red ridge line
def plot_green_line(edge_strength, ridge,gt_row,gt_col):
    sample = []
    sample.append(ridge)
    x = gt_row  # index of the sx value in ridge  282
    y = gt_col  # actual sx value 32
    sampleItr = 0
    toggle = True
    colLst = []
    for j in range(len(edge_strength[0])):
        colLst.append(sum([edge_strength[i][j] for i in range(len(edge_strength))]))
    for itr in range(magic_mcmc_no):
        if (toggle):
            x += 1
        else:
            x -= 1
        temp = list(sample[sampleItr])
        lst = []

        for i in range(len(edge_strength)):  # col = height

            em = emmission_Prob(edge_strength[i][x], colLst[x])
            h = pow((((len(edge_strength) - i) * 0.9) / (len(edge_strength) * 1.0)), 4.6)
            tr = transition_Prob(y, i,5)
            if ((x + 1) == len(ridge) - 1 or (x + 1) == 0):
                trf = pow(transition_Prob(temp[x + 1], i,5), 2)
            else:
                trf = 1
            lst.append(em * h * tr * trf)

        y = lst.index(max(lst))
        temp[x] = y
        sample.append(temp);
        sampleItr += 1;
        if (x == len(ridge) - 1 or x == 0):
            toggle = not toggle
    return sample


# main program - python mountain.py mountain.jpg new_output_file.jpg 0 0
(input_filename, output_filename, gt_row, gt_col) = sys.argv[1:]


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

sample = plot_green_line(edge_strength_value, ridge,int(gt_row),int(gt_col));
imsave(output_filename, draw_edge(input_image, sample[-1], (0, 255, 0), 5))

