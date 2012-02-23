'''
Created on Feb 22, 2012

@author: Moises Osorio [WCoder]
'''
import Gnuplot

class ResultPlotter:

    def __init__(self):
        self.gp = None
        
    def plotSolution(self, solutions, title, subtitle, xlabel, ylabel, zlabel, filename):
        if filename is None:
            self.clear()
        if len(solutions) == 0:
            return
        
        self._startPlotting(title, subtitle, xlabel, ylabel, zlabel)
        idx = 1
        for solution in solutions:
            solutionName = solution[0]
            points = solution[1]
            rgb = solution[2]
            self._plotFile(solutionName, points, rgb, idx)
            idx = idx + 1
        self._endPlotting(filename)
        
    def _startPlotting(self, title, subtitle, xlabel, ylabel, zlabel):
        self.gp = Gnuplot.Gnuplot(persist=0)
        self.gp("set terminal unknown")
        self.gp.title(title + ("" if subtitle is None else "\\n" + subtitle))
        self.gp.xlabel(xlabel)
        self.gp.ylabel(ylabel)
        self.gp.zlabel(zlabel)
        self.gp.plotted = False
        
    def _endPlotting(self, filename):
        self.gp.hardcopy(filename=filename, terminal="png")
        self.gp = None
        
    def _plotFile(self, title, points, color, idx):
#        points.sort()
        self._plot(title, points, color, idx)
        
    def _plot(self, title, points, color, idx):
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
        data.set_option_colonsep("ls", "%d" % idx)
        if "ls" not in data._option_sequence: # HACK!
            data._option_sequence.insert(0, "ls")
            
        rgb = ("#%2x%2x%2x" % (color[0], color[1], color[2])).replace(" ", "0")
        self.gp("set style line %d linecolor rgb \"%s\"" % (idx, rgb))
#        for idx in xrange(1, 1000):
#            
#            s = "set style line %d linecolor rgb \"%s\" lt 3 lw 3" % (idx, rgb)
#            self.gp(s)
#        self.gp("set style line 3 linecolor rgb \"%s\" lt 3 lw 3" % (rgb))
#        self.gp("set style data linecolor rgb \"%s\"" % rgb)
        if self.gp.plotted:
            self.gp.replot(data)
        elif z is None: # 2D
            self.gp.plot(data)
        else: # 3D
            self.gp.splot(data)
        
        self.gp.plotted = True
        