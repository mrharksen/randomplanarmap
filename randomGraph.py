

# Python 2.7.6
# dot - graphviz version 2.36.0 (20140111.2315)
#
#	python randomGraph.py n
#
#	n is the number of vertices in a random tree, default: 100.
#
#	TG
#	13/08/2015
#

import sys
import numpy as np
import scipy.stats as scistats
import networkx as nx
import graphUtil, makeTree, treeToMobile, bdg


# ---------------------------------------------
# ---------------------------------------------


# SETTINGS



# If no argument is given on command line:
n = 100



# If number of vertices was given on command line:
if len( sys.argv ) > 1:

	n = int( sys.argv[1] )


file_name = 'Graph_%d' % n



# Probability distribution xi, should have expected
# value approximately 1.
# Note that if xi(1) == 0, then it is not necessarily possible to
# create a tree with n vertices with the offspring distribution xi.

# xi can be defined as a function...

beta = 2.4788

xi = graphUtil.fatTail( beta )


# ...or as a vector.

#w = [1,0,1]

#xi = graphUtil.equivalentWeights( w )


# The labels on the mobile are determined by mob_lab = 0, 1, 2
# 0 for zeroes
# 1 for deterministic labels
# 2 for random labels
mob_lab = 2



# ---------------------------------------------
# ---------------------------------------------


print 'Make tree...'
T = makeTree.generateTree( xi, n )


print 'Map to mobile...'
M = treeToMobile.treeToMobile( T, labels = mob_lab )


print 'Save mobile...'
graphUtil.saveGraph( M, file_name + 'mobile' )


print 'Map to planar...'
G = bdg.mobileToGraph( M, graphUtil.coin() )




# Appearance
Point = dict(zip( G.nodes(), [ 'point' ] * len(T) ))
Red   = dict(zip( G.nodes(), [ 'red' ] * len(T) ))

nx.set_node_attributes( G, Point, 'shape' )
nx.set_node_attributes( G, Red, 'color' )

G.node[ 'rho' ][ 'color' ] = 'green'




print 'Save planar...'
graphUtil.saveGraph( G, file_name, draw = True, write = False, prog = 'fdp' )


print 'Ok.'
