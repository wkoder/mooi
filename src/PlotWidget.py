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
        
    def plotSolution(self, pareto, solutions, title, xlabel, ylabel, zlabel, filename=None):
        self.clear()
        if pareto is None and len(solutions) == 0:
            return
        
        self._startPlotting(title, xlabel, ylabel, zlabel)
        if pareto is not None:
            self._plotFile(pareto, "Front")
        for solution in solutions:
            self._plotFile(solution, "Solution")
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
            
        print self.gp.plotted
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
        
    def plot2(self, title = "Solutions with PAE Dominance Grid", fileName = "output/pae_solutions_"+time.strftime("%Y-%m-%d"), showGrid = 0, showLabel = 0, test = None): # Creamos la grafica con GNUPlot
        plot = Gnuplot.Gnuplot(persist=1) # Se muestra al usuario
        plot("set terminal png")
        plot("set output '" + fileName + ".png'")
        if showGrid:
            tics = []
            P = self.P
            V = self.speed
            for k in xrange(self.dimension):
                tic = ""
                for i in xrange(-self.tolerance, self.numSolutions+self.tolerance):
                    position = self.minf[k] + self.firstBox[k] * (P**(V*i) - 1) / ((P**V - 1) * (P ** (V*(i-1)) ) )
                    tic += "'" + str(round(position, 1)) + "' " + str(position)
                    #tic += "'" + str(i) + "' " + str(position)
                    #tic += "'' " + str(position)
                    if i < self.numSolutions+self.tolerance-1:
                        tic += ", "
                tics.append(tic)
            if len(tics[0]) > 0:
                plot("set xtics (" + tics[0] + ")")
            if len(tics[1]) > 0:
                plot("set ytics (" + tics[1] + ")")
            plot("set grid")
        points = []
        self.sort()
        for sol in self.solutions:
            points.append(sol.coordinates)
            if showLabel:
                rounded = []
                for x in sol.coordinates:
                    split = str(x).split(".")
                    try:
                        label = split[0] + "."
                        for i in xrange( min( 2, len(split[1]) ) ):
                            label += split[1][i]
                        rounded.append(label)
                    except:
                        print "Split:", split
                plot("set label \"" + str(rounded).replace("'", "") + "\" at " + str(sol.coordinates[0]+0.0001) +", " + str(sol.coordinates[1]))
        for i in xrange(len(points)):
            for j in xrange(len(points[i])):
                points[i][j] *= self.type; # Si type = -1 invierte los puntos, si type = 1 no pasa nada
        front = Gnuplot.Data(points, title = "Solution")
        
        plot.title(title)
        plot.xlabel("Function 1")
        plot.ylabel("Function 2")
        # Si existe el archivo de pareto real lo mostramos tambien
        if test != None and os.path.exists("../pareto_" + test + ".dat"):                                    
            realPoints = []
            fileReal = open("../pareto_" + test + ".dat", "r")
            line = fileReal.readline()
            while line != "":
                p = line.split()
                x = float(p[0])
                y = float(p[1])
                realPoints.append([x, y])
                line = fileReal.readline()
            real = Gnuplot.Data(realPoints, title = "Pareto front", width = "lines")
            plot.plot(front, real)
        else:
            plot.plot(front)
        print "Pareto Front plotted in", fileName + ".png"
        
    def clear(self):
        self.plotPixmap = QPixmap()
        #self.setPixmap(self.plotPixmap)
        self.setText("No plot to show")
        self.setStyleSheet('* { background-color: white }')
        self._removeTemporalFiles()
        
    def _removeTemporalFiles(self):
        for filename in self.tempNames:
            try:
                os.remove(filename)
            except:
                print "Couldn't delete temporal file: %s" % filename
        self.tempNames = []
    