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
from copy import deepcopy
import random
import math

# We've set up a suggested code structure, but feel free to change it. Just
# make sure your code still works with the label.py and pos_scorer.py code
# that we've supplied.
#
class Solver:
	#exemplars = self.read_data("bc.train")
	# Calculate the log of the posterior probability of a given sentence
	#  with a given part-of-speech labeling
	def posterior(self, sentence, label):
		return 0

	def train(self, data):
		
		pass
	#function taken from label.py .Author:	David Crandall
	@staticmethod
	def read_data(fname):
		exemplars = []
		file = open(fname, 'r');
		for line in file:
			data = tuple([w.lower() for w in line.split()])
			exemplars += [ (data[0::2], data[1::2]), ]

		return exemplars

	@staticmethod
	def transitions(exemplars):
		transitions={}
		s1={}
		s2={}
		complex_transitions={}
		complex_trans_count=0
		count=0
		sentence_count=0
		for tup in exemplars:
			for i in range(len(tup[1])-2):
				complex_trans_count+=1
				if (tup[1][i], tup[1][i+2]) in complex_transitions:
					complex_transitions[(tup[1][i], tup[1][i+2])]+=1.0
				else:
					complex_transitions[(tup[1][i], tup[1][i+2])]=1.0
			sentence_count+=1
			if tup[1][0] in s1:
				s1[tup[1][0]]+=1.0
			else:
				s1[tup[1][0]]=1.0
			if tup[1][-1] in s2:
				s2[tup[1][-1]]+=1.0
			else:
				s2[tup[1][-1]]=1.0
			for i in range(len(tup[1])-1):
				count+=1
				if (tup[1][i] , tup[1][i+1]) in transitions:
					transitions[(tup[1][i] , tup[1][i+1])]+=1.0
				else:
					transitions[(tup[1][i] , tup[1][i+1])]=1.0
		
		for i in s1:
			s1[i]=s1[i]/sentence_count
		for i in transitions:
			if i in s2:
				transitions[i]=transitions[i]/(count-s2[i])
			else:
				transitions[i]=transitions[i]/(count)
		
		for i in complex_transitions:
			if i in s2:
				complex_transitions[i]=complex_transitions[i]/(count-s2[i])
			else:
				complex_transitions[i]=complex_transitions[i]/(count)
		#for i in complex_transitions:
		#	if i in s2:
		#		complex_transitions[i] = complex_transitions[i]/(complex_trans_count-s2[i])
		#	else:
		#		complex_transitions[i] = complex_transitions[i]/(complex_trans_count)
		#print count, sentence_count
		return (transitions,s1, complex_transitions)
				
	#calculates the total number of occurences for each word, 
	#divides by total_word_count and stores 
	#the probability in a dictionary
	#returns p(w), p(s_i)
	@staticmethod
	def priors(exemplars):
		total_word_count=0.0
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
		for pos in pos_occurences:
			pos_occurences[pos]/=total_word_count
		return (word_occurences, pos_occurences, total_word_count)

	#calculates the likelihood for each word and pos
	#returns h(w | s_i) for each s_i
	@staticmethod
	def likelihood(exemplars, pos_occurences, total_word_count):
		likelihood={}
		for tup in exemplars:
			for word in range(len(tup[0])):
				if (tup[0][word], tup[1][word]) in likelihood:
					likelihood[(tup[0][word], tup[1][word])]+=1.0
				else:
					likelihood[(tup[0][word], tup[1][word])]=1.0
		for tup in likelihood:
			#print likelihood[tup], pos_occurences[tup[1]]
			likelihood[tup] /=pos_occurences[tup[1]]
			likelihood[tup]/=total_word_count
		return likelihood
	
	#calculates p(s_i|w_i)= p(w_i|s_i)*p(s_i)	
	@staticmethod
	def simple_posterior(word, pos, likelihood, pos_occurences):
		if (word,pos) in likelihood:
			return (math.log(likelihood[(word, pos)]*pos_occurences[pos]), pos)
		else:
			return 0.000000000001
	#calculate the log of the posterior probability of a given sentence
	#  with a given part-of-speech labeling
	def posterior(self, sentence, label):
		return 0
	
	# Functions for each algorithm.
	def simplified(self, sentence):
		exemplars= Solver.read_data("bc.train")
		priors= Solver.priors(exemplars)
		pos_occurences = priors[1]
		likelihood = Solver.likelihood(exemplars, priors[1], priors[2])
		pos_list=[]
		for word in sentence:
			temp=[]
			for pos in pos_occurences:
				if (word,pos) in likelihood:
					temp.append(Solver.simple_posterior(word, pos, likelihood, pos_occurences))
			if not temp:
				temp.append((1, 'noun'))
			temp.sort(key=lambda tup:tup[0], reverse=True)
			pos_list.append(temp[0][1])
		return [ [pos_list], [[0] * len(sentence),] ]

	def hmm(self, sentence):
		exemplars= Solver.read_data("bc.train")
		tr = Solver.transitions(exemplars)	
		priors= Solver.priors(exemplars)
		pos_occurences = priors[1]
		total_word_count = priors[2]
		likelihood = Solver.likelihood(exemplars, pos_occurences, total_word_count)
		pos_list=[[(likelihood[(sentence[0],pos)]*tr[1][pos],pos,pos) if (sentence[0],pos) in likelihood else (0.00000000000001*tr[1][pos]/total_word_count,pos, pos )for pos in pos_occurences]]
		for word in sentence[1:]:
			previous= pos_list[-1]
			current=[]
			for pos in pos_occurences:
				emission = likelihood[(word,pos)] if (word, pos) in likelihood else 0.000000001
				best=[]
				for i in range(len(previous)):
					#print previous[i][1]
					trans_prob = tr[0][(previous[i][1],pos)] if (previous[i][1],pos) in tr[0] else 0.00000000000000000001
					best.append((emission*previous[i][0]*trans_prob,previous[i][1],pos))	
				current.append(max(best))
			#print current
			pos_list.append(current)
		path=[]
		for word_list in pos_list:
			best_val=max(word_list, key=lambda tup:tup[0])
			#print best_val
			path.append(best_val[2])
		return [ [ path], [] ]

	def complex(self, sentence):
		exemplars= Solver.read_data("bc.train")
		tr = Solver.transitions(exemplars)
		second_tr = tr[2]
		#print tr[0], "tr"	
		priors= Solver.priors(exemplars)
		pos_occurences = priors[1]
		total_word_count = priors[2]
		likelihood = Solver.likelihood(exemplars, pos_occurences, total_word_count)
		pos_list=[[(likelihood[(sentence[0],pos)]*tr[1][pos],pos) if (sentence[0],pos) in likelihood else (0.00000000000001*tr[1][pos]/total_word_count,pos)for pos in pos_occurences]]
		second=[]
	
		prev = pos_list[-1]
		for pos in pos_occurences:
			emission = likelihood[(sentence[1],pos)] if (sentence[1], pos) in likelihood else 0.000000001
			
			for i in range(len(prev)):
				trans_prob = tr[(prev[i][1],pos)] if (prev[i][1],pos) in tr else 0.00000000000000000001
				#second_trans_prob = second_tr[(second_prev[i][1],pos)] if (second_prev[i][1],pos) in tr else 0.00000000000000000001
				second.append((prev[i][0]*trans_prob*emission,pos))
		pos_list.append(second)	
		second_prev=pos_list[-2]
		for word in sentence[2:]:
			current=[]
			for pos in pos_occurences:
				emission = likelihood[(word,pos)] if (word, pos) in likelihood else 0.000000001
				for i in range(len(prev)):
					trans_prob = tr[(prev[i][1],pos)] if (prev[i][1],pos) in tr else 0.00000000000000000001
				for i in range(len(second_prev)):
					second_trans_prob = second_tr[(second_prev[i][1],pos)] if (second_prev[i][1],pos) in tr else 0.00000000000000000001
					#print len(second_prev), len(prev)
					current.append((prev[i][0]*trans_prob*second_trans_prob*emission,pos))
			#print len(current)
			pos_list.append(current)	
		#print len(pos_list), len(sentence)
		ls = zip(*(map(max, pos_list)))[1]
		print ls
		mp = zip(*(map(max, pos_list)))[0]
		return [ [ ls], [mp] ]


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

