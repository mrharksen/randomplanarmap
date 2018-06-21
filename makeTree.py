

# Python 2.7.6
# dot - graphviz version 2.36.0 (20140111.2315)
#
#	python makeTree.py
#
#	TG
#	10/08/2015
#
# Packages:
# numpy:		For computation.
# scipy.stats:	For probability distributions.
# networkx:		Graphs.

import numpy as np
import scipy.stats as scistats
import networkx as nx

import graphUtil



def createXi( xi, n, maxiter = 9999 ):
	'''

	Xi = createXi( xi, n )

	In: n is an integer
		xi is a probability distribution on the integers
		(must be able to calculate the probabilities of
		multiple integers at once),
		OR xi is a vector (list, numpy.ndarray, ...)
		such that sum(xi) = 1,
		maxiter is an integer (default maxiter = 999)

	Out: Xi is a random vector such that Xi[i] ~ xi for all i
		and sum(Xi) = n - 1.
		The program crashes if the number of trials exceeds maxiter.

	The algorithm is described in 'Simulating size-constrained
	Galton-Watson trees' by Luc Devroye.

	Note that the algorithm does not necessarily ever stop if the expected
	value of xi is far from 1!

	'''

	# Check if xi is a probability distribution,
	# or else a vector of probabilities.
	if hasattr(xi,'__call__'):

		Multinom = lambda m,zeta: graphUtil.multinomial( m, zeta )

	else:

		Multinom = lambda m,P: np.random.multinomial( m, P )


	# Multinomial method, page 8.

	trials = 0

	while True:

		N = Multinom( n, xi )

		K = len(N)

		trials += 1

		# If sum( j*N[j] ) == n-1, then we are done.
		# If not, then we try again.
		if ( np.arange(K) * N ).sum() == n-1:

			break

		if trials >= maxiter:

			raise RuntimeError('Maximum number of trials reached' +\
								' (%d). ' % maxiter +\
								'Try again or choose another' +\
								' probability distribution.')


	print '\t%d trials' % trials


	# Create a vector with N[j] copies of j
	# for j = 0, ..., K-1 and permute it randomly.
	Xi = np.concatenate([ j * np.ones( N[j] ) for j in range(K) ])
	Xi = np.random.permutation( Xi )

	# Random walk, page 5.

	S = 1	# S_0
	minS = 1
	index = 0

	for t in range( n - 1 ):
		# S_t = S_(t-1) + Xi[t] - 1
		# minS_t = min{r <= t: S_r} = S_index

		S = S + Xi[t+1] - 1 # S_(t+1)

		if S < minS:

			minS = S		#minS_(t+1)

			index = t + 1


	# Rotate Xi such that the random walk ends at 0.
	Xi = np.roll( Xi, -index - 1 )

	return Xi.astype( int )




def makeTree( Xi ):
	'''

	T = makeTree( Xi )

	In: Xi is a list (list, numpy.ndarray,...) of n integers.

	Out: T is a tree (networkx.Graph) with vertices 0, 1, ..., n-1,
		such that vertex number j has Xi[j] children (0 is the root).

	'''

	n = len(Xi)

	T = nx.Graph()

	# Start with the root.
	T.add_node( 0 )
	node_count = 1


	for parent in range(n):
		# The vertex parent has Xi[parent] children,
		# whose numbers are node_count, node_count + 1, ...
		#			..., node_count + Xi[parent] - 1

		children = range( node_count, node_count + Xi[parent] )

		node_count = node_count + Xi[parent]

		# Add the children to the tree and connect to parent.
		T.add_nodes_from(children)

		for child in children:

			T.add_edge(parent,child)


	# Adjust look
	Point = dict(zip( T.nodes(), ['point'] * len(T) ))
	Red =   dict(zip( T.nodes(), ['red'] * len(T) ))
	Blank = dict(zip( T.nodes(), [' '] * len(T) ))

	nx.set_node_attributes( T, Point, 'shape' )
	nx.set_node_attributes( T, Red, 'color' )
	nx.set_node_attributes( T, Blank, 'label' )

	return T




def generateTree( xi, n ):
	'''

	T = generateTree( xi, n ):

	In: n is an integer
		xi is a probability distribution on the integers
		(must be able to calculate the probabilities of
		multiple integers at once),
		OR xi is a vector (list, numpy.ndarray, ...)
		such that sum(xi) = 1,
		maxiter is an integer (default maxiter = 999)

	Out: T is a tree (networkx.Graph) with vertices 0, 1, ..., n-1,
		and xi as offspring distribution.
		P(k children) = xi(k)

	'''

	Xi = createXi( xi, n )

	return makeTree( Xi )





def geoTree( n ):
	'''

	T = geoTree( n )

	In: n >= 1 is an integer.

	Out: T is a simply generated tree with n vertices
		and geometric offspring distribution.
		P(k children) = 0.5^(k+1), k>= 0
	'''

	xi = lambda k: 0.5 ** ( k + 1. ) # Geo

	Xi = createXi( xi, n )

	return makeTree( Xi )




# ---------------------------------------------
# ---------------------------------------------




def main():
	'''

	main()

	Out: An image has been saved, makeTree.png,
		of a 100 vertex random tree.

	'''

	# Probability distribution xi, should have expected
	# value around 1.
	# Can be defined as a function...
	#xi = lambda x: scistats.geom.pmf(x+1,0.5)

	# ...or as a vector.
	w = [572,1,2,3,4,5,6,7,8,9,10,11,12]
	xi = 1.*np.array(w)/sum(w)

	print 'Make tree...'

	T = generateTree( xi, 100 )

	print 'Save...'

	graphUtil.saveGraph( T, 'makeTree' )

	print 'Ok.'




if __name__ == '__main__':
    main()
