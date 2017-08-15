Parts of speech tagging 
=======================

Parts of speech tagging is done in 3 methods:
1. Simplified
2. HMM
3. Complex

Formualation and Abstraction:
-----------------------------
- The simplified model calculates the log of posterior probabilty for each word . i.e. P(S_i | w_i)  = argmax(P(w_i | S_i)*P(S_i))
- P(w_i | S_i) is the likelihood of the word given part of speech(pos). It is basically the percentage of the word in total pos occurences. P(s_i) is the prior of the part of speech. 
- The HMM uses viterbi algorithm. The transitions function calculates P(s_i | S_i-1) . i.e. the transition probability from one tag 
to other.
- For each (word, pos) combination, the arg max of the transitions from previous states is taken. Once the edge weights in the Trellis are computed, the path is backtracked from end to beginning. 
- The complex model uses the forward-backward algorithm for doing variable elimination. It computes P( S_i | w1, w2, ....wn) for each S_i in {S_1...S_n}.However, in this model , there are two transitions we have to consider. i.e. P( S_i | S_i-1) and P( S_i | S_i-2). P(S_i | w1...wn) is proportional to P( w_(i+1)...w_n | S_i)*P(w_1...w_i , S_i). The first part is computed using backward elimination while the second one is done using forward elimination. 

Description of how program works:
---------------------------------
- The likelihood function calculates P(w_i | s_i) for all the words and pos. 
- The priors function calculates P(s_i) and P(w_i) for all words. 
- The transitions calculate P(s_i | S_i-1) and P(s_i | s_i-2) for all possible pos. 
- The simple_posterior function calculates the log of posterior probabilty for each word. 
- The read_data function reads the data. It is directly taken from label.py written by David Crandall. 
- The train function trains the data. train_vals is a global variable in which training information is stored. If train_vals is 0 , the training is done again. 
- The posterior function gives the marginals for a sentence. P(S1,S2,S3,....Sn | W1,W2,....Wn)

Problems, assumptions, simplifications, design decisions:
----------------------------------------------------------

1. Word not present in train data :  
- In the simplified model, the word is considered to be a noun if it's not present in the train data.
- In the other two models, the likelihood for all parts of speech is considered same . i.e. 10 ^-9
2. Transition probabilty not present:
- This doesn't apply to the simplified model. In the other two models, its taken to be 10^-12.
- For simplification, we have used no transition probability in calculating the posterior. i.e. 
```
P(S1...Sn | W1...Wn) = ProductOf(P(w_i | s_i)*P(s_i)) = sum(log(P(w_i | s_i)*P(s_i))) 
```
Results : The word accuracy in all the three models is above 90% . Overall for a corpus of 2000 sentences( bc.test), the program takes about 25-30 seconds. 
