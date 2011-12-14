'''
Created on Dec 11, 2011

@author: Moises Osorio [WCoder]
'''
import math

from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
import numpy
#import time

from Metrics import Metrics

__EPS__ = 1e-6

class MetricsPanel(QWidget):
    '''
    classdocs
    '''
    
    COVERAGE = object()
    ADDITIVE_EPSILON = object()
    MULTIPLICATIVE_EPSILON = object()

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
        
    def updateMetrics(self, optimalPareto, solutions):
        self.table.setColumnCount(len(solutions))
        solutionNames = [solution[0] for solution in solutions]
        self.table.setHorizontalHeaderLabels(solutionNames)
        unary = ['Error ratio', 'Generational distance', 'Spacing']
        binaryTypes = ['Coverage', 'Additive epsilon', 'Multiplicative epsilon']
        binary = []
        for binaryType in binaryTypes:
            binary += ["%s (%s)" % (binaryType, name) for name in solutionNames]
        labels = unary + binary
        self.table.setRowCount(len(labels))
        self.table.setVerticalHeaderLabels(labels)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        mean = [[], [], []]
        std = [[], [], []]
        for column in xrange(len(solutions)):
            values = [[], [], []]
            for solution in solutions[column][1]:
#                tic = time.clock()
                metrics = Metrics(optimalPareto, solution)
#                print time.clock() - tic
#                tic = time.clock()
                values[0].append(metrics.errorRatio())
#                print time.clock() - tic
#                tic = time.clock()
                values[1].append(metrics.generationalDistance())
#                print time.clock() - tic
#                tic = time.clock()
                values[2].append(metrics.spacing())
#                print time.clock() - tic, "\n\n"
#                tic = time.clock()
                
            for m in xrange(len(values)):
                mean[m].append(numpy.mean(values[m]))
                std[m].append(numpy.std(values[m]))

        for metric in [MetricsPanel.COVERAGE, MetricsPanel.ADDITIVE_EPSILON, MetricsPanel.MULTIPLICATIVE_EPSILON]:
            meanMetric, stdMetric = self._getMetric(solutions, metric)
            mean += meanMetric
            std += stdMetric
            
        for row in xrange(len(mean)):
            for column in xrange(len(mean[row])):
                m = mean[row][column]
                s = std[row][column]
                if m is None or s is None:
                    continue
                
                value = "%.6f / %.6f" % (m, s)
                if row < len(unary) and abs(m - min(x for x in mean[row] if x is not None)) < __EPS__:
                    value = "<b>%s</b>" % value
                elif row >= len(unary):
                    offset = row - (row - len(unary)) % len(solutions)
                    factor = 1
                    if row < len(unary) + len(solutions): # Coverage should be maximized
                        factor = -1
                    if m*factor < mean[offset + column][row - offset]*factor:
                        value = "<b>%s</b>" % value
                    
                self._setMetric(row, column, value)
                
        self.table.resizeColumnsToContents()
        
    def _setMetric(self, row, column, value):
        item = QLabel(value)
        item.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row, column, item)

    def _getMetric(self, solutions, metric):
        mean = []
        std = []
        for i in xrange(len(solutions)):
            mean.append([0] * len(solutions))
            std.append([0] * len(solutions))
            for j in xrange(len(solutions)):
                if i == j:
                    mean[i][j] = std[i][j] = None
                    continue
                values = []
                for a in solutions[i][1]:
                    for b in solutions[j][1]:
                        metrics = Metrics(None, a, b)
                        if metric == MetricsPanel.COVERAGE:
                            values.append(metrics.coverage())
                        elif metric == MetricsPanel.ADDITIVE_EPSILON:
                            values.append(metrics.additiveEpsilon())
                        elif metric == MetricsPanel.MULTIPLICATIVE_EPSILON:
                            values.append(metrics.multiplicativeEpsilon())
                mean[i][j] = numpy.mean(values)
                std[i][j] = numpy.std(values)
        return mean, std
    