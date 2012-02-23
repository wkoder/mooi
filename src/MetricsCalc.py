'''
Created on Feb 20, 2012

@author: Moises Osorio [WCoder]
'''
from Metrics import Metrics
import numpy

class MetricsCalc():
        
    COVERAGE = object()
    ADDITIVE_EPSILON = object()
    MULTIPLICATIVE_EPSILON = object()
    __MIN__ = 1
    __MAX__ = -1
    __EPS__ = 1e-6

    def __init__(self):
        self.n = 0
        
    def getLatex(self, fromRow=0, toRow=-1, fromColumn=0, toColumn=-1):
        if toRow == -1:
            toRow = len(self.labels)
        else:
            toRow += 1
        if toColumn == -1:
            toColumn = self.n
        else:
            toColumn += 1
        
        nColumns = toColumn - fromColumn
        latex = ["\\begin{center}"]
        latex.append("    \\begin{table}")
        latex.append("        \\tiny")
        latex.append("        \\begin{tabularx}{\\textwidth}{| X || %s |}" % (" | ".join(["X"] * nColumns)))
        latex.append("            \\hline")
        latex.append("            Metric / Algorithm & " + " & ".join(self.solutionNames[fromColumn:toColumn]) + " \\\\")
        for row in xrange(fromRow, toRow):
            if row == fromRow or row == len(self.labels):
                latex.append("            \\hline \\hline")
            else:
                latex.append("            \\hline")
                
            latexRow = [self.labels[row]]
            for col in xrange(fromColumn, toColumn):
                latexRow.append(self.metricValues[row][col].replace("<b>", "\\textbf{").replace("</b>", "}"))
            latex.append("            " + " & ".join(latexRow) + " \\\\")
        
        latex.append("            \\hline")
        latex.append("        \\end{tabularx}")
        latex.append("    \\end{table}")
        latex.append("\\end{center}")
        return "\n".join(latex)
        
    def computeMetrics(self, optimalPareto, solutions):
        self.solutionNames = [solution[0] for solution in solutions]
        solutionData = [solution[1] for solution in solutions]
        self.dim = len(solutionData[0][0][0])
        self.n = len(self.solutionNames)
        
        unaryMetrics = ['Error ratio', 'Generational distance', 'Spacing', "Hypervolume"]
        unaryMetricType = [MetricsCalc.__MIN__, MetricsCalc.__MIN__, MetricsCalc.__MIN__, MetricsCalc.__MAX__]
        binaryMetrics = ['Coverage', 'Additive epsilon', 'Multiplicative epsilon']
        binaryMetricType = [MetricsCalc.__MAX__, MetricsCalc.__MIN__, MetricsCalc.__MIN__]
        binaryMetricDesc = []
        for binaryMetric in binaryMetrics:
            binaryMetricDesc += ["%s (%s)" % (binaryMetric, name) for name in self.solutionNames]
        self.labels = unaryMetrics + binaryMetricDesc
        self.labels.append("Points")
        nLabels = len(self.labels)
        self.metricValues = [[""] * (self.n + 1) for _ in xrange(nLabels + 1)]
        
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
        for solutionA in xrange(self.n):
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
        
        wins = [0] * self.n
        for row in xrange(len(mean)):
            for column in xrange(len(mean[row])):
                m = mean[row][column]
                s = std[row][column]
                if m is None or s is None:
                    continue
                
                value = "%.6f / %.6f" % (m, s)
                if row < len(unaryMetrics) and abs(m*unaryMetricType[row] - min(x*unaryMetricType[row] for x in mean[row] if x is not None)) < MetricsCalc.__EPS__:
                    value = "<b>%s</b>" % value
                    wins[column] += 1
                elif row >= len(unaryMetrics):
                    offset = row - (row - len(unaryMetrics)) % self.n
                    metricIdx = int((row - len(unaryMetrics)) / self.n)
                    if m*binaryMetricType[metricIdx] > mean[offset + column][row - offset]*binaryMetricType[metricIdx]:
                        value = "<b>%s</b>" % value
                        wins[column] += 1.0 / (self.n - 1)
                
                self.metricValues[row][column] = value
        
        maxValue = max(wins)
        for solutionIdx in xrange(self.n):
            value = "%.2f" % (wins[solutionIdx])
            if abs(wins[solutionIdx] - maxValue) < MetricsCalc.__EPS__:
                value = "<b>%s</b>" % value
            self.metricValues[nLabels-1][solutionIdx] = value
        
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
        return self.n
    
    def getSolutionNames(self):
        return self.solutionNames
    
    def getMetricLabels(self):
        return self.labels
    
    def getMetricValues(self):
        return self.metricValues
    