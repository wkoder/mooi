'''
Created on Dec 11, 2011

@author: Moises Osorio [WCoder]
'''

from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport

class MetricsPanel(QTableWidget):

    def __init__(self, analyzer):
        QWidget.__init__(self)
        self.analyzer = analyzer
        self.metrics = self.analyzer.metrics
        
        corner = self.findChild(QAbstractButton)
        if corner is not None:
            corner.setText("Metric / Algorithm")
            corner.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Paint and isinstance(obj, QAbstractButton): # Looks this is always true
            headerOption = QStyleOptionHeader()
            headerOption.init(obj)
            state = QStyle.State_NoChange
            if obj.isEnabled():
                state |= QStyle.State_Enabled
            
            headerOption.state = state
            headerOption.rect = obj.rect()
            headerOption.text = obj.text()
            headerOption.position = QStyleOptionHeader.OnlyOneSection
            painter = QStylePainter(obj)
            painter.drawControl(QStyle.CE_Header, headerOption)
            return True
        
        return QTableWidget.eventFilter(self, obj, event)
        
    def clear(self):
        self.setRowCount(0)
        self.setColumnCount(0)
        
    def copyMetrics(self):
#        selRange  = self.selectedRanges()[0] # Take the first range
#        topRow = selRange.topRow()
#        bottomRow = selRange.bottomRow()
#        rightColumn = selRange.rightColumn()
#        leftColumn = selRange.leftColumn()
        
        cb = QApplication.clipboard()
        cb.setText(self.analyzer.getCurrentLatex())
        
    def updateMetrics(self, optimalPareto, solutions, functionName):
        self.metrics.computeMetrics(optimalPareto, solutions, functionName)
        
        self.setColumnCount(self.metrics.getNSolutions())
        self.setHorizontalHeaderLabels(self.metrics.getSolutionNames())
        self.setRowCount(len(self.metrics.getMetricLabels()))
        self.setVerticalHeaderLabels(self.metrics.getMetricLabels())
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        for row in xrange(len(self.metrics.metricMean)):
            for column in xrange(len(self.metrics.metricMean[row])):
                decimalFormat = "%.6f"
                if self.metrics.metricStd[row][column] is None:
                    decimalFormat = "%.2f"
                item = QLabel(self.analyzer.getFormattedValue(self.metrics.metricMean[row][column], self.metrics.metricStd[row][column], \
                                                              self.metrics.metricIsBest[row][column], decimalFormat, "<b>%s<\b>"))
                item.setAlignment(Qt.AlignCenter)
                self.setCellWidget(row, column, item)
            
        self.resizeColumnsToContents()
        self.layout()
