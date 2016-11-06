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
'''
Parts of speech tagging is done in 3 methods:
1)Simplified
2)HMM
3)Complex

1) Formualation and Abstraction: 

The simplified model calculates the log of posterior probabilty for each word . i.e. P(S_i | w_i)  = argmax(P(w_i | S_i)*P(S_i))
P(w_i | S_i) is the likelihood of the word given part of speech(pos). It is basically the percentage of the word in total pos occurences. P(s_i) is the prior of the part of speech. 

The HMM uses viterbi algorithm. The transitions function calculates P(s_i | S_i-1) . i.e. the transition probability from one tag 
to other. For each (word, pos) combination, the arg max of the transitions from previous states is taken. Once the edge weights in the Trellis are computed, the path is backtracked from end to beginning. 


The complex model uses the forward-backward algorithm for doing variable elimination. It computes P( S_i | w1, w2, ....wn) for 
each S_i in {S_1...S_n}.However, in this model , there are two transitions we have to consider. i.e. P( S_i | S_i-1) and P( S_i | S_i-2). P(S_i | w1...wn) is proportional to P( w_(i+1)...w_n | S_i)*P(w_1...w_i , S_i). The first part is computed using backward elimination while the second one is done using forward elimination. 

2)Description of how program works:

The likelihood function calculates P(w_i | s_i) for all the words and pos. 
The priors function calculates P(s_i) and P(w_i) for all words. 
The transitions calculate P(s_i | S_i-1) and P(s_i | s_i-2) for all possible pos. 
The simple_posterior function calculates the log of posterior probabilty for each word. 
The read_data function reads the data. It is directly taken from label.py written by David Crandall. 
The train function trains the data. train_vals is a global variable in which training information is stored. If train_vals is 0 , the training is done again. 
The posterior function gives the marginals for a sentence. 

3)Problems, assumptions, simplifications, design decisions:

Scenario 1) Word not present in train data :  
	In the simplified model, the word is considered to be a noun if it's not present in the train data.
	In the other two models, the likelihood for all parts of speech is considered same . i.e. 10 **-9

Scenario 2) Transition probabilty not present:
	This doesn't apply to the simplified model. In the other two models, its taken to be 10**-12. 

Results : The word accuracy in all the three models is above 90% . Overall for a corpus of 2000 sentences( bc.test), the program takes about 25-30 seconds. 
'''
####
from copy import deepcopy
import random
import math

# We've set up a suggested code structure, but feel free to change it. Just
# make sure your code still works with the label.py and pos_scorer.py code
# that we've supplied.
#
class Solver:
	
	train_vals = 0
	posteriors=0
	# Calculate the log of the posterior probability of a given sentence
	#  with a given part-of-speech labeling
	def posterior(self, sentence, label):
		
		return Solver.posteriors
	
	def train(self, data):	
		if Solver.train_vals!=0:
			return Solver.train_vals
		exemplars= Solver.read_data(data)
		tr = Solver.transitions(exemplars)
		second_tr = tr[2]	
		priors= Solver.priors(exemplars)
		pos_occurences = priors[1]
		total_word_count = priors[2]
		likelihood = Solver.likelihood(exemplars, pos_occurences, total_word_count)
		Solver.train_vals = (exemplars, tr, second_tr, priors, pos_occurences, total_word_count, likelihood) 
		return Solver.train_vals
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
	#def posterior(self, sentence, label):
	#	return 0
	
	# Functions for each algorithm.
	def simplified(self, sentence):
		#return [[['noun']*len(sentence)],[[0]*len(sentence)]]
		exemplars, tr, second_tr, priors, pos_occurences, total_word_count, likelihood = self.train('bc.train')
		pos_list, marginals=[],[]
		for word in sentence:
			temp=[]
			for pos in pos_occurences:
				if (word,pos) in likelihood:
					temp.append(Solver.simple_posterior(word, pos, likelihood, pos_occurences))
			if not temp:
				temp.append((1, 'noun'))
			temp.sort(key=lambda tup:tup[0], reverse=True)	
			pos_list.append(temp[0][1])
			marginals.append(sum(zip(*temp)[0]))
		Solver.posteriors= sum(marginals)
		#print "hi", len(pos_list) , len(Solver.posteriors), Solver.posteriors
		return [ [pos_list], [marginals] ]

	def hmm(self, sentence):
		exemplars, tr, second_tr, priors, pos_occurences, total_word_count, likelihood = self.train('bc.train')
		pos_list=[[(math.log(likelihood[(sentence[0],pos)])+math.log(tr[1][pos]),pos,pos) if (sentence[0],pos) in likelihood else (math.log(0.00000000000001)+math.log(tr[1][pos]),pos, pos )for pos in pos_occurences]]
		if len(sentence)==1:
			return [[[max(pos_list[0])[2]]], []]
		for word in sentence[1:]:
			previous= pos_list[-1]
			current=[]
			for pos in pos_occurences:
				emission = math.log(likelihood[(word,pos)]) if (word, pos) in likelihood else math.log(0.000000001)
				best=[]
				for i in range(len(previous)):
					trans_prob = math.log(tr[0][(previous[i][1],pos)] )if (previous[i][1],pos) in tr[0] else math.log(0.00000000000000000001)
					best.append((emission+previous[i][0]+trans_prob,previous[i][1],pos))	
				current.append(max(best))
			pos_list.append(current)
		path=[]
		for word_list in pos_list:
			best_val=max(word_list, key=lambda tup:tup[0])
			path.append(best_val[2])
		return [ [ path], [] ]

	def complex(self, sentence):
		exemplars, tr, second_tr, priors, pos_occurences, total_word_count, likelihood = self.train('bc.train')
		pos_list=[[(likelihood[(sentence[0],pos)]*tr[1][pos],pos) if (sentence[0],pos) in likelihood else (0.00000000000001*tr[1][pos]/total_word_count,pos)for pos in pos_occurences]]
		second=[]
		if len(sentence)==1:
			return [[[max(pos_list[0])[1]]], [[0]*len(sentence)]]
		else:
			prev = pos_list[-1]
			for pos in pos_occurences:
				emission = likelihood[(sentence[1],pos)] if (sentence[1], pos) in likelihood else 0.000000001
				for i in range(len(prev)):
					trans_prob = tr[(prev[i][1],pos)] if (prev[i][1],pos) in tr else 0.00000000000000000001
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
						current.append((prev[i][0]*trans_prob*second_trans_prob*emission,pos))
				pos_list.append(current)	
			ls = zip(*(map(max, pos_list)))[1]
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

