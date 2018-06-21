

# Python 2.7.6
# dot - graphviz version 2.36.0 (20140111.2315)
#
#	python graphUtil.py
#
#	TG
#	14/08/2015
#
# Packages:
# numpy:					For computation.
# networkx:					Graphs.
# pygraphviz:				Visualizing graphs.
# Queue:					markDistance uses Queue.
# scipy.optimize.brentq:	For root finding.
# scipy.special.zeta 		For fat tailed distributions


import numpy as np
import networkx as nx
import pygraphviz as pgv
import Queue
from scipy.optimize import brentq
from scipy.special import zeta as RiemannZeta


def equivalentWeights( w ):
	'''

	p = equivalentWeights( w )

	In: w is a vector (list, numpy.ndarray, ...),
		len(w) > 1 and w[k] > 0 for some k > 0.

	Out: p is a probability weight sequence with expected value 1
		that is equivalent to w in the sense of
		'Simply generated trees, conditioned Galton-Watson trees,
		random allocations and condensation' by Svante Janson.

	'''

	n = len(w)

	w = np.array( w )

	nrange = np.arange( n )


	# f = sum_k (k - 1) * w_k * t^k
	f = lambda z: sum( ( nrange - 1. ) * w * z**nrange )

	# Root search interval
	a = 0
	b = 1.0

	# Ensure that f changes sings on [a,b]
	while f(b) < 0:
		b = 2*b


	# Find the unique root of f on [a,b]
	t = brentq( f, a, b )


	# Phi is the generating function of w
	Phi_t = sum( w * t**nrange )


	# p_k = t^k * w_k / Phi(k)
	return t**nrange * w / Phi_t


def fatTail( c ):
	'''

	xi = fatTail( c )

	In: c is a number in (2, 3).

	Out: xi is a probability distribution on the integers
		with expected value 1.
		There exist a and b such that
			xi(0) = a
			xi(k) = b * k^(-c)

	'''

	b = 1.0 / RiemannZeta( c - 1, 1 )

	a = 1.0 - b * RiemannZeta( c, 1 )

	# Some workaround with boolean values needed:
	return lambda k: (a - b)*(k == 0) + b*( k + (k == 0) )**( - c )



def coin():
	'''

	result = coin()

	UT: result == 1 with probability 0.5
		result == -1 with probability 0.5

	'''

	rand = int(round( np.random.random() ))

	return 1 - 2 * rand



def multinomial( n, xi, max=999 ):
	'''

	N = multinomial( n, xi )

	In: n is an integer
		xi is a probability distribution on the integers
		(must be able to calculate the probabilities of
		multiple integers at once),
		max is an integer (default max =  999).

	Out: N is a Multinomial(n,P) random vector (except the
		trailing zeroes have been trimmed), where P is
		a vector of length max+1 such that P[i] = xi(i)
		for i in {0, ..., max - 1} and P[max] = 1 - sum(P).

	'''

	P = xi( np.arange( max + 1. ) )

	N = np.random.multinomial( n, P )

	return np.trim_zeros( N, 'b' )




def saveGraph( G, filename, draw = True, write = False, prog = 'neato' ):
	'''

	saveGraph( G, filename, draw, write, prog )

	In: G is a graph (networkx.Graph)
		filename is a string
		draw, write are boolean (default True, False)

	UT: If prog is one of
		'neato','dot','twopi','circo','fdp','nop'
		then the graph, G, gets the layout prog and:

			If draw == True, then an image of the graph
			is saved in filename.png.
			Else, if draw == False, no image is saved.

			If write == True, the graph is saved
			in text format in filename.dot.

		Else, if prog is not on the list,
		the graph gets no particular layout and:

			No image of the graph is saved.

			If write == True, the graph is saved
			in text format in filename.dot.

	'''

	progValid = prog in [ 'neato', 'dot', 'twopi', 'circo', 'fdp', 'nop' ]

	if draw and not progValid:
		# Print warning if draw and progValid disagree.

		print 'WARNING: prog = ' + prog \
			+ ' is not one of neato|dot|twopi|circo|fdp|nop.' \
			+ '\n\tNothing is drawn.'

		draw = False


	# Convert the graph from networkx.Graph
	# to pygraphviz.AGraph
	H = nx.nx_agraph.to_agraph( G )


	if progValid:

		print '\tLayout...'

		H.layout(prog=prog)

	if draw:

		print '\tDraw %s.png...' % filename

		H.draw(filename + '.png')

	if write:

		print '\tWrite %s.dot...' % filename

		H.write(filename + '.dot')


	return



def childrenOf( parent, T, grandParent = None ):
	'''

	children = childrenOf( parent, T, grandParent )

	In: T is a tree.
		parent is a vertex in T.
		grandParent is None or a vertex in T such
		that {grandParent,parent} is an edge in T.

	Out: children is a list of all children of parent.
		If grandParent is None, we take parent to be the root of T.
		Else, if {grandParent,parent} is an edge in T,
		we take grandParent to be the parent of parent.

	'''

	children = []


	for v in nx.all_neighbors(T,parent):

		if not v is grandParent:

			children.append(v)

	return children




def markDistance( G, origin, copy = False ):
	'''

	H = markDistance( G, origin, copy )

	In: G is a connected graph.
		origin is a vertex in G.
		copy is boolean (default: False)

	Out: H is the same graph as G, except that
		the 'label' attributes of the vertices have
		been set to be the length of the shortest
		path to origin.

		If copy == True, then H is a new graph and G
		has not been changed.
		Else if copy == False, then H is the same
		object as G and thus, G has been altered.

	'''

	if copy:

		H = G.copy()

	else:

		H = G

	# Initialise all labels.
	Labels = dict(zip( H.nodes(), [-1] * len(H) ))

	nx.set_node_attributes( H, 'label', Labels )

	H.node[origin][ 'label' ] = 0


	Q = Queue.Queue( maxsize = len(G) )
	Q.put( origin )


	# Perform breadth first search to learn
	# all distances to origin.
	while not Q.empty():

		u = Q.get()

		for v in nx.all_neighbors(G,u):

			if H.node[v]['label'] < 0:
				# Hofum fundid nyjan hnut.

				H.node[v]['label'] = H.node[u]['label'] + 1

				Q.put( v )

	return H





def sampleTree():
	'''

	T = sampleTree()

	Out: Returns a very specific 23 vertex graph.

	'''

	T = nx.Graph()

	T.add_nodes_from( range(23) )

	T.add_edge(0,1)
	T.add_edge(0,2)
	T.add_edge(0,3)
	T.add_edge(1,4)
	T.add_edge(1,5)
	T.add_edge(2,6)
	T.add_edge(2,7)
	T.add_edge(3,8)
	T.add_edge(3,9)
	T.add_edge(5,10)
	T.add_edge(5,11)
	T.add_edge(8,12)
	T.add_edge(8,13)
	T.add_edge(8,14)
	T.add_edge(9,15)
	T.add_edge(9,16)
	T.add_edge(10,17)
	T.add_edge(10,18)
	T.add_edge(11,19)
	T.add_edge(13,20)
	T.add_edge(13,21)
	T.add_edge(14,22)

	return T
