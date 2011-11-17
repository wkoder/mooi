'''
Created on Oct 4, 2011

@author: Moises Osorio [WCoder]
'''

import time
import os
import tempfile

import Gnuplot
from PyQt4.QtCore import * #@UnusedWildImport
from PyQt4.QtGui import * #@UnusedWildImport

class PlotWidget(QLabel):
    """A L{QLabel} whose surface is painted with the current plot."""
    def __init__(self):
        QLabel.__init__(self)

        self.tempNames = []
        self.gp = None

        self.setAlignment(Qt.AlignCenter)
        self.clear()
        
    def plotSolution(self, solutions, title, xlabel, ylabel, zlabel, filename=None):
        self.clear()
        if len(solutions) == 0:
            return
        
        self._startPlotting(title, xlabel, ylabel, zlabel)
        for solutionName in solutions.keys():
            self._plotFile(solutions[solutionName], solutionName)
        self._endPlotting(filename)
        
    def _startPlotting(self, title, xlabel, ylabel, zlabel):
        self.gp = Gnuplot.Gnuplot(persist=0)
        self.gp("set terminal unknown")
        self.gp.title(title)
        self.gp.xlabel(xlabel)
        self.gp.ylabel(ylabel)
        self.gp.zlabel(zlabel)
        self.gp.plotted = False
        
    def _endPlotting(self, filename=None):
        tmp = filename is None
        if tmp:
            filename = tempfile.mkstemp(prefix="mooi_", suffix=".png", text=False)[1]
        self.gp.hardcopy(filename=filename, terminal="png")
        self.gp = None
        if tmp:
            self.tempNames.append(filename)
            self.setPlotPixmap(filename)
        
    def _plotFile(self, filename, title):
        points = []
        f = open(filename, "r")
        for line in f:
            point = [float(x) for x in line.split()]
            if len(point) > 0:
                points.append(point)
        points.sort()
        self._plot(points, title)
        
    def _plot(self, points, title):
        x = []
        y = []
        z = None
        for point in points:
            x.append(point[0])
            y.append(point[1])
            if len(point) >= 3:
                if z is None:
                    z = []
                z.append(point[2])
                
        if z is None:
            data = Gnuplot.Data(x, y, title=title)
        else:
            data = Gnuplot.Data(x, y, z, title=title)
            
        if self.gp.plotted:
            self.gp.replot(data)
        elif z is None: # 2D
            self.gp.plot(data)
        else: # 3D
            self.gp.splot(data)
        
        self.gp.plotted = True
        
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
        self._removeTemporalFiles()
        
    def clear(self):
        self.plotPixmap = QPixmap()
        #self.setPixmap(self.plotPixmap)
        self.setText("No plot to show")
        self.setStyleSheet('* { background-color: white }')
        
    def _removeTemporalFiles(self):
        for filename in self.tempNames:
            try:
                os.remove(filename)
            except:
                print "Couldn't delete temporal file: %s" % filename
        self.tempNames = []
    