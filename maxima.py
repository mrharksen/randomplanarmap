
#
# Python 2.7.6
# dot - graphviz version 2.36.0 (20140111.2315)
#
#	python maxima.py
#
#	Byr til slembinet a ferhyrningsgerd og telur fjolda alpha-omega para.
#
#
#	TG
#	12/08/2015
#


import sys
import numpy as np
import scipy.stats as scistats
import Queue
import networkx as nx
import graphUtil, makeTree, treeToMobile, bdg


# ---------------------------------------------
# ---------------------------------------------

def isUniverse( G, alpha, d ):
	'''
	
	omega = isUniverse( G, alpha, d )


	G er net 
	alpha er hnutur i netinu
	d er thvermal netsins G

	Ef omega == alpha, tha er G ekki alheimur med upphaf alpha.
	Annars er G alheimur med upphaf alpha og endalok omega.


	'''


	dist = dict( zip( G.nodes(), [-1] * len(G) ) )

	# d(alpha,alpha) = 0
	dist[alpha] = 0


	Q = Queue.Queue( maxsize=len(G) )
	Q.put( alpha )


	# Perform breadth first search to learn
	# all distances to alpha.
	while not Q.empty():

		u = Q.get()

		if dist[u] == d:
			# Ef u er i maximal fjarlaegd og enn eru hnutar
			# i rodinni, tha eru their allir i maximal fjarlaegd.
			# Faum thvi ekki alheim.
			# Ef u er i maximal fjarlaegd og enginn hnutur er i
			# rodinni, tha er hann eina stb. hagildid i G.
			if Q.empty():
				return u
			else:
				return alpha
		
		isMax = True

		neighbors = nx.all_neighbors(G,u)

		for v in neighbors:
			 
			
			# Ef vid hofum ekki heimsott v adur,
			# tha latum vid hann i rodina.
			if dist[v] == -1:
				dist[v] = dist[u] + 1
				Q.put(v)

			# Ef d(alpha,v) > d(alpha,u)
			# tha er u ekki stb. hagildi.
			if dist[v] > dist[u]:
				isMax = False

		# Haettum ef vid hofum fundid stb. hagildi sem
		# er ekki i maximal fjarlaegd fra alpha.
		if isMax:
			return alpha
	



# ---------------------------------------------
# ---------------------------------------------


# Oddatala
n = 101

w = [1,0,1]

xi = 1. * np.array(w) / sum(w) 

mob_lab = 1

# ---------------------------------------------
# ---------------------------------------------

#print 'Make tree...'
T = makeTree.generateTree(xi,n)

#print 'Map to mobile...'
M = treeToMobile.treeToMobile( T, mob_lab )

#print 'Map to planar...'
G = bdg.mobileToGraph( M, graphUtil.coin() )


# ---------------------------------------------
# ---------------------------------------------


#graphUtil.saveGraph( G, 'maxim', draw = True, write = False, prog = 'fdp' )


Nodes = G.nodes()

d = nx.diameter(G)

count = 0


# Skodum alla hnuta i G og vitum hvort their myndi upphof.
for u in Nodes:

	v = isUniverse(G,u,d)
	
	if not u == v:
		# Ef u og v eru olik, tha er G u-v alheimur
		# og vid thurfum ekki ad skoda v.
	
		count += 1
		Nodes.remove(v)



print 'Fjoldi para: %d' % count
