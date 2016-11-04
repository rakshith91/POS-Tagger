import random
# initial sample -- assigned arbitrarily
# we're using 0="red", 1="green" here
(E, G, L) = (0, 0, 0)
samples = []
for n in range(0, 10000):
# first sample a new value of G given L and E
	G = L if random.random() < 0.75 else 1-L
# now sample from P(L | E,G) given E and G.
# First figure out this distribution:
# P_red = P(L=red, E, G)/P(E,G)
# P_green = P(L=green, E, G) / P(P,G)
L_dist = ( 0.3 * (0.75 if 0 == G else 0.25) * (0.9 if 0 == E else 0.1),
0.7 * (0.75 if 1 == G else 0.25) * (0.9 if 1 == E else 0.1) )
# instead of actually figuring out P(P,G), just normalize P_red and P_green so that they sum to 1
L = 0 if (random.random() < L_dist[0] / sum(L_dist) ) else 1
samples += [(E, G, L),]
print (E, G, L)
print samples
G_green_count = sum( [ g for (e, g, l) in samples ] )
L_green_count = sum( [ l for (e, g, l) in samples ] )
print "P(G=green | E=red) = " + str(G_green_count / float(len(samples))) + \
", actual: " + str( (0.3 * 0.25 * 0.9 + 0.7 * 0.75 * 0.1) / ( 0.7 * 0.1 + 0.3 * 0.9 ) )
print "estimated P(L=green | E=red) = " + str(L_green_count / float(len(samples))) + \
", actual: " + str( 0.1*0.7 / (0.1*0.7 + 0.9*0.3) )