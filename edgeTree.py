import sys
import numpy as np
import scipy.stats as scistats
import networkx as nx
import graphUtil, makeTree, treeToMobile, bdg


def findContourLeaves(contSeq, T):
    contLeaves = []
    for x in contSeq:
        if T.degree(x) == 1:
            contLeaves.append(x)
    if contLeaves[0] != 0:
        contLeaves.append(contLeaves[0])
    return contLeaves

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

T = makeTree.generateTree( xi, n )
graphUtil.saveGraph( T, 'edgeTree' )
rootT = min( T.nodes() )
contSeq = []
bdg.findContourSequence( contSeq, T, rootT, None )
contLeaves = findContourLeaves(contSeq, T)
G = T
for i in range(len(contLeaves)-1):
    G.add_edge(contLeaves[i],contLeaves[i+1])
graphUtil.saveGraph( G, 'edgeGraph' )
