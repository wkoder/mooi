'''
Created on Oct 4, 2011

@author: Moises Osorio [WCoder]
'''

from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport
import time

class PlotWidget(QLabel):
    """A L{QLabel} whose surface is painted with the current plot."""
    def __init__(self):
        QLabel.__init__(self)

        self.setAlignment(Qt.AlignCenter)
        self.clear()
        
    def setPlotPixmap(self, filename):
        # try for 13 times (1.3 second total) before giving up
        counter = 13
        while not self.plotPixmap.load(filename) and counter > 0:
            time.sleep(0.1)
            counter = counter - 1
            
        if counter == 0:
            self.setText("Error while plotting, try again.")
        else:
            self.setPixmap(self.plotPixmap)
        
    def clear(self):
        self.plotPixmap = QPixmap()
        self.setText("No plot to show")
        self.setStyleSheet('* { background-color: white }')
        