'''
Created on Dec 11, 2011

@author: Moises Osorio [WCoder]
'''

from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
import numpy
import time

from Metrics import Metrics

class MetricsPanel(QWidget):
    '''
    classdocs
    '''

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
        self.table.setRowCount(3)
        self.table.setColumnCount(len(solutions))
        self.table.setHorizontalHeaderLabels([solution[0] for solution in solutions])
        self.table.setVerticalHeaderLabels(['Error ratio', 'Generational distance', 'Spacing'])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        mean = [[], [], []]
        std = [[], [], []]
        for column in xrange(len(solutions)):
            values = [[], [], []]
            for solution in solutions[column][1]:
                tic = time.clock()
                metrics = Metrics(optimalPareto, solution)
                print time.clock() - tic
                tic = time.clock()
                values[0].append(metrics.errorRatio())
                print time.clock() - tic
                tic = time.clock()
                values[1].append(metrics.generationalDistance())
                print time.clock() - tic
                tic = time.clock()
                values[2].append(metrics.spacing())
                print time.clock() - tic, "\n\n"
                tic = time.clock()
                
            for m in xrange(len(values)):
                mean[m].append(numpy.mean(values[m]))
                std[m].append(numpy.std(values[m]))
                
        for row in xrange(len(mean)):
            for column in xrange(len(mean[row])):
                m = mean[row][column]
                s = std[row][column]
                value = "%.6f / %.6f" % (m, s)
                if abs(m - min(mean[row])) < 1e-6:
                    value = "<b>%s</b>" % value
                    
                self._setMetric(row, column, value)
                
        self.table.resizeColumnsToContents()
        
    def _setMetric(self, row, column, value):
        item = QLabel(value)
        self.table.setCellWidget(row, column, item)
