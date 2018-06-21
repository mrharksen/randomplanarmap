

# Python 2.7.6
# dot - graphviz version 2.36.0 (20140111.2315)
#
#	python bdg.py
#	
#	TG
#	11/08/2015
#
# Packages:
# networkx:		Graphs

import networkx as nx

import treeToMobile
import graphUtil





def findContourSequence( contSeq, T, node, parent ):
	'''

	findContourSequence( contSeq, T, node, parent )
	
	In:	contSeq is a list
		T is a tree such that for each node, its
		children appear in ascending order from left
		to right in the plane.
		node and parent are nodes in T,
		except if parent == None, in which case node
		is the root of T.

	Out: node and all its descendants (assuming parent is
		the parent of node) have been added to contSeq 
		(with repetition) in the order they appear in a 
		clockwise walk around the subtree induced by node
		and its	descendants.
	
	'''

	contSeq.append( node )

	children = graphUtil.childrenOf( node, T, parent )

	# Ensure that the children are visited in the correct order.
	children.sort()

	# Recursively finish the objective for each child of node.
	for child in children:

		findContourSequence( contSeq, T, child, node )


	# If node is not the root, walk back to its parent.
	if not parent is None:

		contSeq.append( parent )




def successor( i, c, l ):
	'''

	j = successor( i, c, l )
	
	In:	i is an integer, c is the white contour sequence
		of a tree with an added vertex 'rho' at the end.
		l is a dictionary of labels.

	Out: j is the successor of i:
		 j = inf{ j > i: l[c[j]] == l[c[i]] - 1 }
	
		Note that we take inf{} to be -1, because c[-1] == 'rho'.
	
	'''

	# The period of the sequence c is m = len(c) - 1
	# (the last element is ignored):
	m = len(c) - 1

	# Find the next j > i such that c[j] has the following label:
	label = l[c[i]] - 1
	
	for k in range( 1, m ):
		# We have tried
		# j = i+1, i+2, ..., i+k-1

		# The index is calculated modulo m
		j = (i + k) % m

		if l[c[ j ]] == label:

			return j
	
	# If no such j exists, then we return the index of 'rho'.
	return -1




def mobileToGraph( M, eps = 1 ):
	'''

	G = mobileToGraph( M, eps )
	
	In: M is a labeled mobile whose vertices are integers.
		We take the minimal vertex to be the root of M.
		eps is either -1 or 1.

	Out: G is the bipartite planar map corresponding
		to (M,eps) according to the inverse BDG bijection
		described in 'Scaling limits of random planar maps
		with a unique large face' by S.O.S and S.J.

		The marked vertex in G is 'rho'. 
		The root edge has the attribute 'awayFrom' which
		is set to be either one of its endpoints.
	
	'''

	n = nx.number_of_edges( M )

	rootM = min( M.nodes() )


	# Make a list of the nodes of M encountered
	# on a clockwise walk around the tree.
	contSeq = []

	findContourSequence( contSeq, M, rootM, None )


	# The white contour sequence is defined by
	# wcs[k] = contSeq[2*k]
	# We know that contSeq[-1] == contSeq[0],
	# so the last element is unnecessary.
	wcs = contSeq[:-1:2]


	# Add an external vertex, 'rho',
	# at the end of wcs.
	# (It has "infinite" index, -1)
	wcs.append( 'rho' )


	# Create a new empty graph, G, out of the white vertices in M
	# and the external vertex 'rho'.
	G = nx.MultiGraph()

	G.add_nodes_from( wcs )


	# Make a dictionary, lab, for the labels of the mobile M
	# such that for each node u in M, lab[u] is the label of u in M.
	lab = {}

	for node in G.nodes():

		if node == 'rho': continue

		lab[node] = M.node[node][ 'label' ]


	# Put an edge between each wcs[i] and its successor, wcs[j],
	# where j is found by the successor function.
	for i in range(n):

		G.add_edge( wcs[i], wcs[ successor( i, wcs, lab ) ] )

	
	# Decorate the special node in G.
	G.node[ 'rho' ][ 'color' ] = 'green'


	# The root edge in G is the first edge between the root of M
	# and its successor.
	rootSucc = wcs[ successor( 0, wcs, lab ) ]

	rootG = G[ rootM ][ rootSucc ][0]
	

	# Decorate the root edge and determine its direction.
	rootG['color'] = 'blue'

	if eps > 0:

		rootG['awayFrom'] = rootSucc

	else:

		rootG['awayFrom'] = rootM


	return G




def main():
	'''

	main()
	
	Out: Three images have been saved,
		1) A bipartite Halin graph, bdg_halin0.png
		2) Its corresponding mobile, bdg_mobile.png
		3) The planar map corresponding to the mobile, bdg_halin1.png.
			Note: not necessarily the same graph as 1), since
			the BDG bijection depends on the embedding of the graph.

	'''

	
	# Make a mobile
	T = graphUtil.sampleTree()
	
	M = treeToMobile.treeToMobile( T, labels = 2 )

	# Map the mobile to a graph.
	G = mobileToGraph( M, eps = graphUtil.coin() )

	graphUtil.saveGraph( M, 'bdg_M' )
	graphUtil.saveGraph( G, 'bdg_G' )





if __name__ == '__main__':
	main()
