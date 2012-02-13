'''
Created on Dec 11, 2011

@author: Moises Osorio [WCoder]
'''

from Metrics import Metrics
from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
import numpy


__EPS__ = 1e-6

class MetricsPanel(QWidget):
    '''
    classdocs
    '''
    
    COVERAGE = object()
    ADDITIVE_EPSILON = object()
    MULTIPLICATIVE_EPSILON = object()
    __MIN__ = 1
    __MAX__ = -1

    def __init__(self):
        '''
        Constructor
        '''
        QWidget.__init__(self)
        self.table = QTableWidget()
        radioLayout = QHBoxLayout()
        radioLayout.addWidget(self.table)
        self.setLayout(radioLayout)
        
    def clear(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        
    def copyMetrics(self):
        selRange  = self.table.selectedRanges()[0] # Take the first range
        topRow = selRange.topRow()
        bottomRow = selRange.bottomRow()
        rightColumn = selRange.rightColumn()
        leftColumn = selRange.leftColumn()
        nColumns = rightColumn - leftColumn + 1
        clipStr = QString("\\begin{center}\n")
        clipStr.append("    \\begin{tabular}{| l || %s |}\n" % (" | ".join(["c"] * nColumns)))
        clipStr.append("        \\hline\n")
        clipStr.append("        M\\'{e}trica / Algoritmo & " + " & ".join(str(self.table.horizontalHeaderItem(col).text()) \
                                                   for col in xrange(leftColumn, rightColumn+1)) + " \\\\\n")
        clipStr.append("        \\hline \\hline\n")
        for row in xrange(topRow, bottomRow+1):
            clipStr.append(self.table.verticalHeaderItem(row).text())
            for col in xrange(leftColumn, rightColumn+1):
                clipStr.append(QString(" & "))
                cell = self.table.cellWidget(row, col)
                if cell:
                    clipStr.append(cell.text().replace("<b>", "\\textbf{").replace("</b>", "}"))
            clipStr.append("\\\\\n")
        
        clipStr.append("        \\hline\n")
        clipStr.append("    \\end{tabular}\n")
        clipStr.append("\\end{center}\n")
        cb = QApplication.clipboard()
        cb.setText(clipStr)
        
    def updateMetrics(self, optimalPareto, solutions):
        solutionNames = [solution[0] for solution in solutions]
        solutionData = [solution[1] for solution in solutions]
        dim = len(solutionData[0][0][0])
        
        self.table.setColumnCount(len(solutionNames))
        self.table.setHorizontalHeaderLabels(solutionNames)
        unaryMetrics = ['Error ratio', 'Generational distance', 'Spacing', "Hypervolume"]
        unaryMetricType = [MetricsPanel.__MIN__, MetricsPanel.__MIN__, MetricsPanel.__MIN__, MetricsPanel.__MAX__]
        binaryMetrics = ['Coverage', 'Additive epsilon', 'Multiplicative epsilon']
        binaryMetricType = [MetricsPanel.__MAX__, MetricsPanel.__MIN__, MetricsPanel.__MIN__]
        binaryMetricDesc = []
        for binaryMetric in binaryMetrics:
            binaryMetricDesc += ["%s (%s)" % (binaryMetric, name) for name in solutionNames]
        labels = unaryMetrics + binaryMetricDesc
        labels.append("Winnings")
        self.table.setRowCount(len(labels))
        self.table.setVerticalHeaderLabels(labels)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        nadirPoint = [-(1<<30)] * dim
        for solution in solutionData:
            for run in solution:
                for point in run:
                    for d in xrange(dim):
                        nadirPoint[d] = max(nadirPoint[d], 2*point[d]) # Make it twice far
        
        metrics = Metrics(optimalPareto, solutionData)
        metrics.setHypervolumeReference(nadirPoint)
        mean = [[], [], [], []]
        std = [[], [], [], []]
        for solutionA in xrange(len(solutionData)):
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

        for metric in [MetricsPanel.COVERAGE, MetricsPanel.ADDITIVE_EPSILON, MetricsPanel.MULTIPLICATIVE_EPSILON]:
            meanMetric, stdMetric = self._getMetric(solutionData, metric, metrics)
            mean += meanMetric
            std += stdMetric
            
        wins = [0] * len(solutionNames)
        for row in xrange(len(mean)):
            for column in xrange(len(mean[row])):
                m = mean[row][column]
                s = std[row][column]
                if m is None or s is None:
                    continue
                
                value = "%.6f / %.6f" % (m, s)
                if row < len(unaryMetrics) and abs(m*unaryMetricType[row] - min(x*unaryMetricType[row] for x in mean[row] if x is not None)) < __EPS__:
                    value = "<b>%s</b>" % value
                    wins[column] += 1
                elif row >= len(unaryMetrics):
                    offset = row - (row - len(unaryMetrics)) % len(solutionData)
                    metricIdx = int((row - len(unaryMetrics)) / len(solutionData))
                    if m*binaryMetricType[metricIdx] > mean[offset + column][row - offset]*binaryMetricType[metricIdx]:
                        value = "<b>%s</b>" % value
                        wins[column] += 1.0 / len(solutionNames)
                    
                self._setMetric(row, column, value)
                
        maxValue = max(wins)
        for solutionIdx in xrange(len(solutionNames)):
            value = "%.2f" % (wins[solutionIdx])
            if abs(wins[solutionIdx] - maxValue) < __EPS__:
                value = "<b>%s</b>" % value
            self._setMetric(len(labels)-1, solutionIdx, value)
            
        self.table.resizeColumnsToContents()
        
    def _setMetric(self, row, column, value):
        item = QLabel(value)
        item.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row, column, item)

    def _getMetric(self, solutionData, metric, metrics):
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
                        if metric == MetricsPanel.COVERAGE:
                            values.append(metrics.coverage())
                        elif metric == MetricsPanel.ADDITIVE_EPSILON:
                            values.append(metrics.additiveEpsilon())
                        elif metric == MetricsPanel.MULTIPLICATIVE_EPSILON:
                            values.append(metrics.multiplicativeEpsilon())
                mean[a][b] = numpy.mean(values)
                std[a][b] = numpy.std(values)
        return mean, std
    