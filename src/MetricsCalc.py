'''
Created on Feb 20, 2012

@author: Moises Osorio [WCoder]
'''
from Metrics import Metrics
import numpy
import types

class MetricsCalc():
        
    COVERAGE = object()
    ADDITIVE_EPSILON = object()
    MULTIPLICATIVE_EPSILON = object()
    __MIN__ = 1 # Metric to minimize
    __MAX__ = -1 # Metric to maximize
    __CONV__ = 1 # Convergence metric
    __DIST__ = 2 # Distribution metric
    __EPS__ = 1e-6

    def __init__(self):
        self.nSolutions = None
        
    def computeMetrics(self, optimalPareto, solutions):
        self.solutionNames = [solution[0] for solution in solutions]
        solutionData = [solution[1] for solution in solutions]
        self.dim = len(solutionData[0][0][0])
        self.nSolutions = len(self.solutionNames)
        
        unaryMetrics = ['Error ratio', 'Generational distance', 'Spacing', "Hypervolume"]
        unaryMetricOptType = [MetricsCalc.__MIN__, MetricsCalc.__MIN__, MetricsCalc.__MIN__, MetricsCalc.__MAX__]
        unaryMetricType = [MetricsCalc.__CONV__, MetricsCalc.__CONV__, MetricsCalc.__DIST__, [MetricsCalc.__CONV__, MetricsCalc.__DIST__]]
        self.nUnaryMetrics = len(unaryMetrics)
        binaryMetrics = ['Coverage', 'Additive epsilon', 'Multiplicative epsilon']
        binaryMetricOptType = [MetricsCalc.__MAX__, MetricsCalc.__MIN__, MetricsCalc.__MIN__]
        binaryMetricType = [MetricsCalc.__CONV__, MetricsCalc.__CONV__, MetricsCalc.__CONV__]
        self.nBinaryMetrics = len(binaryMetrics)
        self.labels = []
        self.sublabels = []
        self.labels += unaryMetrics
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
        self.metricIsBest = [[False] * (self.nSolutions) for _ in xrange(nLabels)]
        
        nadirPoint = [-(1<<30)] * self.dim
        for solution in solutionData:
            for run in solution:
                for point in run:
                    for d in xrange(self.dim):
                        value = point[d] * (2 if point[d] > 0 else 0.5)
                        nadirPoint[d] = max(nadirPoint[d], value) # Make it twice far
        
        metrics = Metrics(optimalPareto, solutionData)
        metrics.setHypervolumeReference(nadirPoint)
        mean = [[], [], [], []]
        std = [[], [], [], []]
        for solutionA in xrange(self.nSolutions):
            values = [[], [], [], []]
            for runA in xrange(len(solutionData[solutionA])):
                metrics.setSolutionsToCompare(solutionA, runA, None, None)
                values[0].append(metrics.errorRatio())
                values[1].append(metrics.generationalDistance())
                values[2].append(metrics.spacing())
                values[3].append(metrics.hypervolume())
                
            for m in xrange(len(values)):
                mean[m].append(numpy.mean(values[m]))
                std[m].append(numpy.std(values[m]))

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
                
                if row < len(unaryMetrics) and abs(m*unaryMetricOptType[row] - min(x*unaryMetricOptType[row] for x in mean[row] if x is not None)) < MetricsCalc.__EPS__:
                    self.metricIsBest[row][column] = True
                    self._addMetricPoints(1.0, column, unaryMetricType[row])
                elif row >= len(unaryMetrics):
                    offset = row - (row - len(unaryMetrics)) % self.nSolutions
                    metricIdx = int((row - len(unaryMetrics)) / self.nSolutions)
                    if m*binaryMetricOptType[metricIdx] > mean[offset + column][row - offset]*binaryMetricOptType[metricIdx]:
                        self.metricIsBest[row][column] = True
                        self._addMetricPoints(1.0 / (self.nSolutions - 1), column, binaryMetricType[metricIdx])
                
                self.metricMean[row][column] = m
                self.metricStd[row][column] = s
        
        row = nLabels - 2
        for points in [self.convPoints, self.distPoints]:
            maxValue = max(points)
            for solutionIdx in xrange(self.nSolutions):
                value = points[solutionIdx]
                if abs(value - maxValue) < MetricsCalc.__EPS__:
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
#                print "Calculating %s of %s and %s" % (metric, solutionNames[a], solutionNames[b])
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
    