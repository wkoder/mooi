'''
Created on Dec 11, 2011

@author: Moises Osorio [WCoder]
'''

from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
from MetricsCalc import MetricsCalc

class MetricsPanel(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.table = QTableWidget()
        radioLayout = QHBoxLayout()
        radioLayout.addWidget(self.table)
        self.setLayout(radioLayout)
        self.metrics = MetricsCalc()
        
    def clear(self):
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        
    def copyMetrics(self):
        selRange  = self.table.selectedRanges()[0] # Take the first range
        topRow = selRange.topRow()
        bottomRow = selRange.bottomRow()
        rightColumn = selRange.rightColumn()
        leftColumn = selRange.leftColumn()
        
        cb = QApplication.clipboard()
        cb.setText(self.metrics.getLatex(topRow, bottomRow, leftColumn, rightColumn))
        
    def updateMetrics(self, optimalPareto, solutions):
        self.metrics.computeMetrics(optimalPareto, solutions)
        
        self.table.setColumnCount(self.metrics.getNSolutions())
        self.table.setHorizontalHeaderLabels(self.metrics.getSolutionNames())
        self.table.setRowCount(len(self.metrics.getMetricLabels()))
        self.table.setVerticalHeaderLabels(self.metrics.getMetricLabels())
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        for row in xrange(len(self.metrics.getMetricValues())):
            for column in xrange(len(self.metrics.getMetricValues()[row])):
                self._setMetric(row, column, self.metrics.getMetricValues()[row][column])
            
        self.table.resizeColumnsToContents()
        
    def _setMetric(self, row, column, value):
        item = QLabel(value)
        item.setAlignment(Qt.AlignCenter)
        self.table.setCellWidget(row, column, item)
