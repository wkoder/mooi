'''
Created on Oct 4, 2011

@author: Moises Osorio [WCoder]
'''

import time
import os
import tempfile

import Gnuplot
from PyQt4 import QtGui
from PyQt4 import QtCore

class PlotWidget(QtGui.QLabel):
    """A L{QLabel} whose surface is painted with the current plot."""
    def __init__(self):
        QtGui.QLabel.__init__(self)

        self.__tempNames = []

        self.setAlignment(QtCore.Qt.AlignCenter)
        self.plotPixmap = QtGui.QPixmap()
        self.setPixmap(self.plotPixmap)
        self.setStyleSheet('QLabel { background-color: white }')
        
    def plotFile(self, filename):
        points = []
        f = open(filename, "r")
        for line in f:
            point = [float(x) for x in line.split()]
            if len(point) > 0:
                points.append(point)
        self.plot(points)
        
    def plot(self, points):
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
            data = Gnuplot.Data(x, y)
        else:
            data = Gnuplot.Data(x, y, z)
        gp = Gnuplot.Gnuplot(persist=0)
        gp("set terminal unknown")
        gp.title("Points")
        gp.xlabel("F1")
        gp.ylabel("F2")
        if z is not None: # 3D
            gp.zlabel("F3")
            gp.splot(data);
        else: # 2D
            gp.plot(data);

        tmp = tempfile.mkstemp(prefix="mooi_", suffix=".png", text=False)[1]
        gp.hardcopy(filename=tmp, terminal="png")
        self.removeTemporalFiles()
        self.__tempNames.append(tmp)
        self.setPlotPixmap(tmp)

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
        
    def removeTemporalFiles(self):
        for filename in self.__tempNames:
            try:
                os.remove(filename)
            except:
                print "Couldn't delete temporal file: %s" % filename
        self.__tempNames = []
    