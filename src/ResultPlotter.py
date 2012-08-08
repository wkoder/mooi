'''
Created on Feb 22, 2012

@author: Moises Osorio [WCoder]
'''
import Gnuplot
import tempfile
import os
import sys

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
        
    def plotIndicators(self, results, title, subtitle, xlabel, ylabel, filename):
        if filename is None:
            self.clear()
        if len(results) == 0:
            return
        
        idx = 0
        xtics = ""
        fd, tempfilename = tempfile.mkstemp(prefix="data", suffix=".dat", text=True)
        data = os.fdopen(fd, 'w')
        minAll = 1e9
        maxAll = -1e9
        for result in results:
            idx += 1
            solutionName = result[0]
            #rgb = result[2]
            if idx > 1:
                xtics += ", "
            xtics += "'%s' %d" % (solutionName, idx)

            values = result[1]
            minAll = min(minAll, values[0])
            maxAll = max(maxAll, values[4])
            data.write("%d %s\n" % (idx, " ".join(str(f) for f in values)))
        data.close()

        self._startPlotting(title, subtitle, xlabel, ylabel, None)
        self.gp("set boxwidth 0.2 absolute")
        self.gp("set xrange [ %d : %d ] noreverse nowriteback" % (0, len(results)+1))
        margin = 0.2 * (maxAll - minAll)
        self.gp("set yrange [ %f : %f ] noreverse nowriteback" % (minAll-margin, maxAll+margin))
        self.gp("set xtics (%s)" % xtics)
        self.gp("plot '%s' using 1:3:2:6:5 with candlesticks lt 3 lw 2 notitle whiskerbars, '' using 1:4:4:4:4 with candlesticks lt -1 lw 2 notitle" % \
                (tempfilename))
        self.gp("set terminal pngcairo")
        self.gp("set output '%s'" % filename)
        self.gp("replot")
        self.gp = None
        #self._endPlotting(filename)
        
        try:
            os.remove(tempfilename)
        except:
            print >> sys.stderr, "Couldn't delete temporal file: %s" % tempfilename
            
        
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
        