'''
Created on Dec 11, 2011

@author: Moises Osorio [WCoder]
'''

from __future__ import division

from momet import *

class Metrics(object):

    def __init__(self, optimal, solutions):
        self.momet = Momet()
        if optimal is not None:
            self.paretoOptimal = self._convertToDDList(optimal)
        self.functions = []
        for solution in solutions:
            runs = []
            for run in solution:
                runs.append(self._convertToDDList(run))
            self.functions.append(runs)
        
    def setSolutionsToCompare(self, a, aIdx, b, bIdx):
        self.a = a
        self.aIdx = aIdx
        self.b = b
        self.bIdx = bIdx
            
    def setHypervolumeReference(self, ref):
        self.hypervolumeReference = self._convertToDList(ref)
            
    def _convertToDDList(self, solution):
        ll = ddList()
        for x in solution:
            ll.append(self._convertToDList(x))
        return ll
    
    def _convertToDList(self, x):
        l = dList()
        map(l.append, x)
        return l
        
    def errorRatio(self):
        """
        Computes the error ratio from the obtained solution set to the optimal Pareto front.
        """
        return self.momet.errorRatio(self.functions[self.a][self.aIdx], self.paretoOptimal)
        
    def generationalDistance(self):
        """
        Computes the generational distance from the obtained solution set to the optimal Pareto front.
        """
        return self.momet.generationalDistance(self.functions[self.a][self.aIdx], self.paretoOptimal)

    def spacing(self):
        """
        Computes the spacing of the obtained solution set.
        """
        return self.momet.spacing(self.functions[self.a][self.aIdx])
        
    def hypervolume(self):
        """
        Computes the hypervolume value of the obtained solution set.
        """
        return self.momet.hypervolume(self.functions[self.a][self.aIdx], self.hypervolumeReference)

    def coverage(self):
        """
        Computes the coverage value of two obtained solution sets.
        """
        return self.momet.coverage(self.functions[self.a][self.aIdx], self.functions[self.b][self.bIdx])
        
    def additiveEpsilon(self):
        """
        Computes the additive epsilon indicator from one obtained solution set to other solution set.
        """
        return self.momet.additiveEpsilon(self.functions[self.a][self.aIdx], self.functions[self.b][self.bIdx])

    def multiplicativeEpsilon(self):
        """
        Computes the multiplicative epsilon indicator from one obtained solution set to other solution set.
        """
        return self.momet.multiplicativeEpsilon(self.functions[self.a][self.aIdx], self.functions[self.b][self.bIdx])
    