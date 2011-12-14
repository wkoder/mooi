'''
Created on Dec 11, 2011

@author: Moises Osorio [WCoder]
'''

from __future__ import division

import numpy

import Utils

class Metrics(object):
    '''
    classdocs
    '''

    def __init__(self, optimal, solutionA, solutionB = None):
        '''
        Constructor
        '''
        if optimal is not None:
            self.paretoOptimal = [numpy.array(a) for a in optimal]
        self.solutionA = [numpy.array(a) for a in solutionA]
        if solutionB is not None:
            self.solutionB = [numpy.array(a) for a in solutionB]
        
    def errorRatio(self):
        """
        Computes the error ratio from the obtained solution set to the optimal Pareto front.
        """
        errors = 0
        for a in self.solutionA:
            for o in self.paretoOptimal:
                if Utils.dominates(o, a):
                    errors += 1
                    break
                
        return errors / len(self.solutionA)
        
    def generationalDistance(self):
        """
        Computes the generational distance from the obtained solution set to the optimal Pareto front.
        """
        power = 2
        s = sum(min([numpy.linalg.norm(a-o, power) for o in self.paretoOptimal]) ** power for a in self.solutionA)
            
        return s ** (1.0 / power) / len(self.solutionA)

    def spacing(self):
        """
        Computes the spacing of the obtained solution set.
        """
        mean = sum(Utils.nearestNeighborDistance(self.solutionA, i) for i in xrange(len(self.solutionA))) / len(self.solutionA)
        s = sum((mean - Utils.nearestNeighborDistance(self.solutionA, i)) ** 2 for i in xrange(len(self.solutionA)))
        return (s / (len(self.solutionA) - 1)) ** 0.5

    def coverage(self):
        """
        Computes the coverage value of two obtained solution sets.
        """
        dominated = 0
        for b in self.solutionB:
            for a in self.solutionA:
                if Utils.weaklyDominates(a, b):
                    dominated += 1
                    break
                
        return dominated / len(self.solutionB)
        
    def additiveEpsilon(self):
        """
        Computes the additive epsilon indicator from one obtained solution set to other solution set.
        """
        dist = []
        for a in self.solutionA:
            dist.append([max(a - b) for b in self.solutionB])
        
        column = lambda mat,c: [mat[i][c] for i in xrange(len(mat))]
        return max(min(column(dist, c)) for c in xrange(len(dist[0])))

    def multiplicativeEpsilon(self):
        """
        Computes the multiplicative epsilon indicator from one obtained solution set to other solution set.
        """
        dist = []
        for a in self.solutionA:
            dist.append([max(a / b) for b in self.solutionB])
            
        column = lambda mat,c: [mat[i][c] for i in xrange(len(mat))]
        return max(min(column(dist, c)) for c in xrange(len(dist[0])))
    