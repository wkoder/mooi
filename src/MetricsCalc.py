'''
Created on Feb 20, 2012

@author: Moises Osorio [WCoder]
'''
from Metrics import Metrics
import Utils

import math
import sys
import numpy
from scipy.stats import scoreatpercentile
import types
from symbol import factor

class MetricsCalc():
        
    COVERAGE = object()
    ADDITIVE_EPSILON = object()
    MULTIPLICATIVE_EPSILON = object()
    __MIN__ = 1 # Metric to minimize
    __MAX__ = -1 # Metric to maximize
    __CONV__ = 1 # Convergence metric
    __DIST__ = 2 # Distribution metric

    def __init__(self):
        self.nSolutions = None
        
    def _removeDominatedFromSolutionData(self, solutions):
        for solution in solutions:
            for r in xrange(len(solution)):
                run = solution[r]
                nr = len(run)
                nd = []
                fromn = len(run)
                for i in xrange(nr):
                    dominated = False
                    for j in xrange(nr):
                        if i != j and Utils.dominates(run[j], run[i]):
                            dominated = True
                            break
                    if not dominated:
                        nd.append(run[i])
                solution[r] = nd
                
                ton = len(nd)
                if fromn != ton:
                    print "From %d to %d points" % (fromn, ton)
        return solutions
        
    def computeMetrics(self, optimalPareto, solutions):
        self.solutionNames = [solution[0] for solution in solutions]
        solutionData = [solution[1] for solution in solutions]
        #solutionData = self._removeDominatedFromSolutionData([solution[1] for solution in solutions])
        self.dim = len(solutionData[0][0][0])
        self.nSolutions = len(self.solutionNames)
        metrics = Metrics(optimalPareto, solutionData)
        
        self.unaryMetricNames = ['Inverted Generational Distance', 'Delta P', \
                        'Spacing', "Hypervolume"]
        unaryMetricOptType = [MetricsCalc.__MIN__, MetricsCalc.__MIN__, \
                              MetricsCalc.__MIN__, MetricsCalc.__MAX__]
        unaryMetricType = [MetricsCalc.__CONV__, MetricsCalc.__CONV__, \
                           MetricsCalc.__DIST__, [MetricsCalc.__CONV__, MetricsCalc.__DIST__]]
        unaryMetricFunction = [metrics.invertedGenerationalDistance, metrics.deltaP, \
                               metrics.spacing, metrics.hypervolume]
        self.nUnaryMetrics = len(self.unaryMetricNames)
        binaryMetrics = ['Coverage', 'Additive Epsilon', 'Multiplicative Epsilon']
        binaryMetricOptType = [MetricsCalc.__MAX__, MetricsCalc.__MIN__, MetricsCalc.__MIN__]
        binaryMetricType = [MetricsCalc.__CONV__, MetricsCalc.__CONV__, MetricsCalc.__CONV__]
        self.nBinaryMetrics = len(binaryMetrics)
        self.labels = []
        self.sublabels = []
        self.labels += self.unaryMetricNames
        self.sublabels += [None] * len(self.labels)
        for binaryMetric in binaryMetrics:
            self.labels += [binaryMetric] * self.nSolutions
            self.sublabels += self.solutionNames
            
        self.labels.append("Points")
        self.sublabels.append("Convergence")
        self.labels.append("Points")
        self.sublabels.append("Distribution")
        
        nLabels = len(self.labels)
        self.metricMean = [[None] * (self.nSolutions) for _ in xrange(nLabels)]
        self.metricStd = [[None] * (self.nSolutions) for _ in xrange(nLabels)]
        self.metricMin = [[None] * (self.nSolutions) for _ in xrange(nLabels)]
        self.metricMax = [[None] * (self.nSolutions) for _ in xrange(nLabels)]
        self.metricQ1 = [[None] * (self.nSolutions) for _ in xrange(nLabels)]
        self.metricQ3 = [[None] * (self.nSolutions) for _ in xrange(nLabels)]
        self.metricIsBest = [[False] * (self.nSolutions) for _ in xrange(nLabels)]
        
        nadirPoint = [-(1<<30)] * self.dim
        for solution in solutionData:
            r = 0
            for run in solution:
                r += 1
                for point in run:
                    for d in xrange(self.dim):
                        nadirPoint[d] = max(nadirPoint[d], math.ceil(point[d] * 10 + Utils.__EPS__) / 10.0)
        print "    Using Nadir point: " + str(nadirPoint)
        metrics.setHypervolumeReference(nadirPoint)
        maxHypervolume = metrics.maxHypervolume()
        
        mean = Utils.createListList(self.nUnaryMetrics)
        std = Utils.createListList(self.nUnaryMetrics)
        mmin = Utils.createListList(self.nUnaryMetrics)
        mmax = Utils.createListList(self.nUnaryMetrics)
        q1 = Utils.createListList(self.nUnaryMetrics)
        q3 = Utils.createListList(self.nUnaryMetrics)
        for solutionA in xrange(self.nSolutions):
            values = Utils.createListList(self.nUnaryMetrics)
            for runA in xrange(len(solutionData[solutionA])):
                metrics.setSolutionsToCompare(solutionA, runA, None, None)
                for i in xrange(self.nUnaryMetrics):
                    value = unaryMetricFunction[i]()
                    if self.unaryMetricNames[i] == "Hypervolume":
                        value /= maxHypervolume
                        if value > 1:
                            print >> sys.stderr, "    Normalized hypervolume of %s exceeds 100%!" % \
                                (self.solutionNames[solutionA])
                    values[i].append(value)
                
            for m in xrange(len(values)):
                mean[m].append(numpy.mean(values[m]))
                std[m].append(numpy.std(values[m]))
                mmin[m].append(numpy.min(values[m]))
                mmax[m].append(numpy.max(values[m]))
                q1[m].append(scoreatpercentile(values[m], 25))
                q3[m].append(scoreatpercentile(values[m], 75))

        for metric in [MetricsCalc.COVERAGE, MetricsCalc.ADDITIVE_EPSILON, MetricsCalc.MULTIPLICATIVE_EPSILON]:
            meanMetric, stdMetric = self._getMetric(solutionData, metric, metrics, self.solutionNames)
            mean += meanMetric
            std += stdMetric
        
        self.convPoints = [0] * self.nSolutions
        self.distPoints = [0] * self.nSolutions
        for row in xrange(len(mean)):
            for column in xrange(len(mean[row])):
                m = mean[row][column]
                s = std[row][column]
                if m is None or s is None:
                    continue
                
                if row < len(self.unaryMetricNames):
                    factor = unaryMetricOptType[row]
                    if abs(round(m*factor, Utils.__ROUND__) - 
                           round(min(x*factor for x in mean[row] if x is not None), Utils.__ROUND__)) < Utils.__EPS__:
                        self.metricIsBest[row][column] = True
                    for i in xrange(len(mean[row])):
                        if i != column and mean[row][i] is not None and \
                                round(mean[row][column]*factor, Utils.__ROUND__) <= round(mean[row][i]*factor, Utils.__ROUND__):
                            self._addMetricPoints(1.0 / (self.nSolutions - 1), column, unaryMetricType[row])
                elif row >= len(self.unaryMetricNames):
                    offset = row - (row - len(self.unaryMetricNames)) % self.nSolutions
                    metricIdx = int((row - len(self.unaryMetricNames)) / self.nSolutions)
                    factor = binaryMetricOptType[metricIdx]
                    if round(m*factor, Utils.__ROUND__) >= round(mean[offset + column][row - offset]*factor, Utils.__ROUND__):
                        self.metricIsBest[row][column] = True
                        self._addMetricPoints(1.0 / (self.nSolutions - 1), column, binaryMetricType[metricIdx])
                
                self.metricMean[row][column] = m
                self.metricStd[row][column] = s
                if row < len(self.unaryMetricNames):
                    self.metricMin[row][column] = mmin[row][column]
                    self.metricMax[row][column] = mmax[row][column]
                    self.metricQ1[row][column] = q1[row][column]
                    self.metricQ3[row][column] = q3[row][column]
        
        row = nLabels - 2
        for points in [self.convPoints, self.distPoints]:
            maxValue = max(points)
            for solutionIdx in xrange(self.nSolutions):
                value = points[solutionIdx]
                if abs(value - maxValue) < Utils.__EPS__:
                    self.metricIsBest[row][solutionIdx] = True
                self.metricMean[row][solutionIdx] = value
            row += 1
            
    def _addMetricPoints(self, points, resultId, metricType):
        isList = isinstance(metricType, types.ListType)
#        if isList:
#            points /= len(metricType)
        if metricType == MetricsCalc.__CONV__ or (isList and MetricsCalc.__CONV__ in metricType):
            self.convPoints[resultId] += points
        if metricType == MetricsCalc.__DIST__ or (isList and MetricsCalc.__DIST__ in metricType):
            self.distPoints[resultId] += points
        
    def _getMetric(self, solutionData, metric, metrics, solutionNames):
        n = len(solutionData)
        mean = []
        std = []
        for a in xrange(n):
            mean.append([0] * n)
            std.append([0] * n)
            for b in xrange(n):
                if a == b:
                    mean[a][b] = std[a][b] = None
                    continue
                
                values = []
                for aIdx in xrange(len(solutionData[a])):
                    for bIdx in xrange(len(solutionData[b])):
                        metrics.setSolutionsToCompare(a, aIdx, b, bIdx)
                        if metric == MetricsCalc.COVERAGE:
                            values.append(metrics.coverage())
                        elif metric == MetricsCalc.ADDITIVE_EPSILON:
                            values.append(metrics.additiveEpsilon())
                        elif metric == MetricsCalc.MULTIPLICATIVE_EPSILON:
                            values.append(metrics.multiplicativeEpsilon())
                mean[a][b] = numpy.mean(values)
                std[a][b] = numpy.std(values)
        return mean, std
    
    def getNDimensions(self):
        return self.dim
    
    def getNSolutions(self):
        return self.nSolutions
    
    def getSolutionNames(self):
        return self.solutionNames
    
    def getMetricLabels(self):
        return self.labels
    