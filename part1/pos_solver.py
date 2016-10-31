###################################
# CS B551 Fall 2016, Assignment #3
#
# Your names and user ids:
#Sairam Rakshith Bhyravabhotla	bsairamr
#Harish Annavajjala				hannavaj
#Jeffrey Peter					jeffravi
#
# (Based on skeleton code by D. Crandall)
#
#
####
# Put your report here!!
####

import random
import math

# We've set up a suggested code structure, but feel free to change it. Just
# make sure your code still works with the label.py and pos_scorer.py code
# that we've supplied.
#
class Solver:

	#function taken from label.py .Author:	David Crandall
	def read_data(self,fname):
		exemplars = []
		file = open(fname, 'r');
		for line in file:
			data = tuple([w.lower() for w in line.split()])
			exemplars += [ (data[0::2], data[1::2]), ]

		return exemplars

	#calculates the total number of occurences for each word, 
	#divides by total_word_count and stores 
	#the probability in a dictionary
	def priors(self, exemplars):
		total_word_count=0
		word_occurences,pos_occurences={},{}
		for tup in exemplars:
			for word in tup[0]:
				total_word_count+=1
				if word in word_occurences:
					word_occurences[word]+=1
				else:
					word_occurences[word]=1
			for pos in tup[1]:
				if pos in pos_occurences:
					pos_occurences[pos]+=1
				else:
					pos_occurences[pos]=1
		return (word_occurences, pos_occurences, total_word_count)

	#calculates the likelihood for each word and pos
	def likelihood(self, exemplars):
		likelihood={}
		for tup in exemplars:
			for word in range(len(tup[0])):
				if (tup[0][word], tup[1][word]) in likelihood:
					likelihood[(tup[0][word], tup[1][word])]+=1
				else:
					likelihood[(tup[0][word], tup[1][word])]=1
		return likelihood

	# Calculate the log of the posterior probability of a given sentence
	#  with a given part-of-speech labeling
	def posterior(self, sentence, label):
		return 0

	# Do the training!
	#
	def train(self, data):
		pass

	# Functions for each algorithm.
	#
	def simplified(self, sentence):
		exemplars= self.read_data("bc.train")
		print self.likelihood(exemplars)
		return [ [ [ "noun" ] * len(sentence)], [[0] * len(sentence),] ]

	def hmm(self, sentence):
		return [ [ [ "noun" ] * len(sentence)], [] ]

	def complex(self, sentence):
		return [ [ [ "noun" ] * len(sentence)], [[0] * len(sentence),] ]


	# This solve() method is called by label.py, so you should keep the interface the
	#  same, but you can change the code itself. 
	# It's supposed to return a list with two elements:
	#
	#  - The first element is a list of part-of-speech labelings of the sentence.
	#	 Each of these is a list, one part of speech per word of the sentence.
	#
	#  - The second element is a list of probabilities, one per word. This is
	#	 only needed for simplified() and complex() and is the marginal probability for each word.
	#
	def solve(self, algo, sentence):
		if algo == "Simplified":
			return self.simplified(sentence)
		elif algo == "HMM":
			return self.hmm(sentence)
		elif algo == "Complex":
			return self.complex(sentence)
		else:
			print "Unknown algo!"

