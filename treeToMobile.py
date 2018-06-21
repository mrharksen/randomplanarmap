

# Python 2.7.6
# dot - graphviz version 2.36.0 (20140111.2315)
#
#	python treeToMobile.py
#
#	TG
#	13/08/2015
#
# Packages:
# Queue:		relabelTree and treeBijection use Queue
# networkx:		Graphs
# numpy:		For computation


import Queue
import networkx as nx
import numpy as np

import graphUtil



def relabelTree( T, root ):
	'''

	S = relabelTree( T, root )

	In: T is a tree with vertices 0, 1, ..., n-1 and root is a vertex in T.
		Each vertex in T has an integer 'age' attribute such that siblings
		have different ages.
		We take siblings to be drawn in ascending order by age from left to
		right in the plane.

	Out: S is a new tree that is just like T, except the vertices have been
		relabeled to 0, 1, ..., n-1 such that the root is 0 and for each
		vertex its children are in ascending order from left to right,
		all vertices in generation <=k are smaller than all vertices in
		generation >k (for all k).

	'''

	n = nx.number_of_nodes( T )

	# Dictionary for the new labels.
	newLabels = dict(zip( range(n), range(n) ))

	nextLabel = 0

	Q = Queue.Queue( maxsize = n )

	Q.put( ( root, None ) )

	while not Q.empty():
		# We have found labels for all the nextLabel vertices
		# that are not descendants of the vertices in the queue Q.

		# The next vertex, node, gets the next number.
		node, parent = Q.get()

		newLabels[node] = nextLabel

		nextLabel = nextLabel + 1

		# Put each child of node on the queue in ascending order by age.
		children = graphUtil.childrenOf( node, T, parent )

		children.sort( key = lambda child: T.node[child][ 'age' ] )

		for child in children:

			Q.put( ( child, node ) )


	# Relabel the vertices according to the dictionary.
	return nx.relabel_nodes( T, newLabels )




def biggestBlueChild( node, T, M ):
	'''

	Used by treeBijection

	blueChild = biggestBlueChild( node, T, M )

	In: T is a tree with integer vertices
		and M is a forest with the same set of vertices.
		node is a vertex in T and M.
		If node has a parent in T, then that parent is red in M.

	Out: blueChild is the largest child of node that has its
		'color' attribute not set to 'red'

	'''

	# Note that None < x for all numbers x.
	blueChild = None

	for v in nx.all_neighbors( T, node ):

		if M.node[v][ 'color' ] != 'red' and blueChild < v:

			blueChild = v


	return blueChild





def treeBijection( T ):
	'''

	M = treeBijection( T )

	In: T is a tree with vertices 0, 1, ..., n-1 such that
		the children of each vertex are larger than the vertex itself
		(and thus the smalles vertex, 0, is the root of T).

	Out: M is a tree, with the same set of vertices as T, that is
		made by the bijection described in 'Recurrence of bipartite
		planar maps' by S.O.S. and J.E.B.
		The vertices in M are ordered such that 0 is the root,
		the children of each vertex are in ascending from left to right,
		all vertices in generation <=k are smaller than all vertices
		in generation >k (for all k).

	'''

	# Create a new empty graph with the same set of vertices as T.
	M = nx.Graph()

	M.add_nodes_from( T.nodes(), color = 'blue', age = 0 )


	# Connect the nodes in M
	Q = Queue.Queue( maxsize = len(T) )

	Q.put( 0 )

	while not Q.empty():

		node = Q.get()

		# Color node red.
		M.node[node][ 'color' ] = 'red'

		# Find the largest child of node in T, that is not red in M.
		next = biggestBlueChild( node, T, M )

		# If no such child exists, then we are done.
		if next is None:
			continue

		# Create a list of blue descendants of node to be colored red.
		bloodLine = [ node ]

		# Add to the list until we find a leaf.
		while T.degree( next ) > 1:

			# Color the next vertex red.
			M.node[next][ 'color' ] = 'red'

			bloodLine.append(next)

			# Find the largest child of next in T that is not red in M.
			next = biggestBlueChild( next, T, M )



		# We have found a leaf.
		leaf = next

		M.node[leaf][ 'color' ] = 'red'


		# Give it an 'age' attribute.
		M.node[leaf][ 'age' ] = nx.degree( M, node )


		# We only use this if this is the first iteration of the loop.
		isFirst = M.node[leaf][ 'age' ] == 0

		if isFirst:
			rootM = leaf


		# Connect the leaf to the vertices in bloodLine
		# and put them all to the queue.
		for i in range(len( bloodLine )):

			u = bloodLine[i]

			M.add_edge( leaf, u )

			M.node[u][ 'age' ] = M.node[u][ 'age' ] + i + isFirst

			Q.put( u )



	# Relabel the vertices in M such that they obey the rules.
	M = relabelTree( M, rootM )

	return M





def colorMobile( M, node ):
	'''

	colorMobile( M, node )

	In: M is a tree and node is a vertex in M.
		Either M.node[node][ 'shape' ] == 'circle'
		or M.node[node][ 'shape' ] == 'point'

	Out: The 'shape' attributes of all descendants of node
		have been altered, such that every second generation
		has the same 'shape' as node and the other generations
		have the "opposite" 'shape'.

		Ironically, the 'color' attribute has not been changed.

	'''

	if M.node[node][ 'shape' ] == 'point':

		shape = 'circle'

	else:

		shape = 'point'


	for v in nx.all_neighbors( M, node ):

		# If we have not already, we color v and all its descendants.
		if not M.node[v][ 'shape' ] == shape:

			M.node[v][ 'shape' ] = shape

			colorMobile( M, v )





def labelMobileDet( M, odd, parent ):
	'''

	labelMobileDet( M, odd, parent )

	In: M is a mobile.
		odd and parent are vertices in M.
		{odd,parent} is an edge in M.
		odd is of an odd generation (and thus,
		parent is of even generation).
		parent has already been given a label.

	Out: All descendants of odd of even generation
		have been given a label by the (-1)-rule.

	'''

	# The labels are determined by the label of odd's parent.
	parentLabel = M.node[parent][ 'label' ]

	# The children to be labeled.
	children = graphUtil.childrenOf( odd, M, parent )

	# Make sure that the children get the labels in the correct order.
	children.sort()

	# Label odd's children.
	for i in range(len( children )):

		v = children[i]

		# The next vertex gets a label that is
		# one less than the preceding vertex.
		M.node[v][ 'label' ] = parentLabel - i - 1

		# Find all children of v (they are of an odd generation)
		# and label them.
		childrenOf_v = graphUtil.childrenOf( v, M, odd )

		for child_v in childrenOf_v:
			labelMobileDet( M, child_v, v )



def labelMobileRand( M, odd, parent ):
	'''

	labelMobileRand( M, odd, parent )

	In: M is a mobile.
		odd and parent are vertices in M.
		{odd,parent} is an edge in M.
		odd is of an odd generation (and thus,
		parent is of even generation).
		parent has already been given a label.

	Out: All descendants of odd of even generation
		have been given a random label.

	'''

	# The children to be labeled.
	children = graphUtil.childrenOf( odd, M, parent )

	# Make sure that the children get the labels in the correct order.
	children.sort()

	n = len(children)

	if n == 0:
		return

	# Make use of the multinomial method to get labels
	# such that the differences of nearby labels are
	# i.i.d.

	# Maximum number of trials:
	maxiter = 999

	# Probability distribution of jumps + 1:
	xi = lambda k: 0.5 ** ( k + 1. )


	trials = 0

	while True:

		N = graphUtil.multinomial( n + 1, xi )

		K = len(N)

		trials += 1

		# If sum( (j-1)*N[j] ) == 0, then we are done.
		# If not, try again.
		if ( ( np.arange(K) - 1 ) * N ).sum() == 0:

			break

		if trials >= maxiter:

			raise RuntimeError('Maximum number of trials reached' +\
								' (%d). ' % maxiter +\
								'Try again or choose another' +\
								'probability distribution.')


	# Create a vector with N[j] copies of j
	# for j = 0, ..., K-1 and permute it randomly.
	Jumps = np.concatenate([ ( j - 1 ) * np.ones( N[j] ) for j in range(K) ])

	Jumps = np.random.permutation( Jumps ).astype( int )

	# Now, Jumps is a vector of n + 1 independent random variables
	# distributed by f(k) = 0.5^(k+2) for k >= -1 and sum(Jumps) == 0.

	# The labels are determined by the label of odd's parent.
	currentLabel = M.node[parent][ 'label' ]

	# Label odd's children.
	for i in range(len( children )):

		v = children[i]

		currentLabel =  currentLabel + Jumps[i]

		M.node[v][ 'label' ] = currentLabel

		# Find all children of v (they are of an odd generation)
		# and label them.
		childrenOf_v = graphUtil.childrenOf( v, M, odd )

		for child_v in childrenOf_v:

			labelMobileRand( M, child_v, v )





def makeMobile( T, root, labels = 0, color = True ):
	'''

	makeMobile( T, root, labels )

	In: T is a tree with 'root' as root.
		labels is an integer (default 0).
		color is a boolean (default True).

	Out: T has been changed into a labeled mobile
		with root as root and the labels are...
			... all 0 if labels == 0.
			... selected deterministically if labels == 1.
			... selected randomly if labels == 2.
		If color == True, then T has been colored by treeToMobile.colorMobile.

	'''

	if color:

		# Initialise
		Square = dict(zip( T.nodes(), [ 'square' ] * len(T) ))
		Black = dict(zip( T.nodes(), [ 'black' ] * len(T) ))
		nx.set_node_attributes( T, Square, 'shape' )
		nx.set_node_attributes( T, Black, 'color' )

		# Make the root special.
		T.node[root][ 'color' ] = 'red'
		T.node[root][ 'shape' ] = 'circle'

		colorMobile( T, root )


	# Initialise all labels to zero.
	Zero = dict(zip( T.nodes(), [0] * len(T) ))

	nx.set_node_attributes( T, Zero, 'label' )


	if labels == 1:

		for v in nx.all_neighbors( T, root ):

			labelMobileDet( T, v, root )

	elif labels == 2:

		for v in nx.all_neighbors( T, root ):

			labelMobileRand( T, v, root )






def treeToMobile( T, labels = 0, color = True ):
	'''

	M = treeToMobile( T, root, labels )

	In: T is a tree with vertices 0, 1, ..., n-1 such that
		the children of each vertex are larger than the vertex itself
		(and thus the smalles vertex, 0, is the root of T).

	Out: M is a tree, with the same set of vertices as T, that is
		made by the bijection described in 'Recurrence of bipartite
		planar maps' by S.O.S. and J.E.B.
		The vertices in M are ordered such that 0 is the root,
		the children of each vertex are in ascending from left to right,
		all vertices in generation <=k are smaller than all vertices
		in generation >k (for all k).

		M is a labeled mobile and the labels are...
			... all 0 if labels == 0.
			... selected deterministically if labels == 1.
			... selected randomly if labels == 2.
		If color == True, then T has been colored by treeToMobile.colorMobile.

	'''

	M = treeBijection( T )

	makeMobile( M, 0, labels, color = color )

	return M




# ---------------------------------------------
# ---------------------------------------------

def main():
	'''

	main()

	Out: An image, treeToMobile.png, of a mobile
		has been saved

	'''

	T = graphUtil.sampleTree()

	M = treeToMobile( T, 2 )

	graphUtil.saveGraph( T, 'tree' )

	graphUtil.saveGraph( M, 'treeToMobile' )



if __name__ == '__main__':
	main()
