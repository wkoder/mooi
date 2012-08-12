'''
Created on Feb 21, 2012

@author: Moises Osorio [WCoder]
'''
from MOSolution import MOSolution
from Metrics import Metrics
from MetricsCalc import MetricsCalc
from ResultPlotter import ResultPlotter
import Utils
import dircache
import os
import types
import sys

class Analyzer:
    
    __PARETO__ = "pareto"
    __IMAGES_DIR__ = "images/"
    
    def __init__(self, plotterTerminal="png"):
        self.plotter = ResultPlotter(plotterTerminal)
        self.metrics = MetricsCalc()
        
        self.pareto = None
        self.setResultDirectories([])
        
    def setPareto(self, pareto):
        self.pareto = pareto
        self.addResultDirectory(pareto)
        
    def addResultDirectory(self, result):
        if result not in self.resultDirectories:
            self.nResults += 1
            self.resultDirectories.append(result)
            self.resultNames.append(self.getResultName(result))
            self._scanDirectory(result)
        
    def removeResultDirectory(self, result):
        if result in self.resultDirectories:
            self.resultDirectories.remove(result)
            self.setResultDirectories(self.resultDirectories)
        
    def setResultDirectories(self, results):
        self.resultDirectories = []
        self.resultNames = []
        self.functions = {}
        self.nResults = 0
        
        if self.pareto is not None:
            self.setPareto(self.pareto)
        for result in results:
            self.addResultDirectory(result)
        
    def getResultName(self, directory):
        directory = str(directory)
        if directory[-1] == "/":
            directory = directory[:-1]
        slash = max(directory.rfind("/"), directory.rfind("\\"))
        return directory[slash+1:]
    
    def getResultsForFunction(self, functionName):
        return self.functions[functionName.lower()]
    
    def getFunctionNames(self, includeNotSolved=False):
        return [function.functionName for function in self.functions.values() if includeNotSolved or \
                self._hasNonPareto(function.functionImplementation) or \
                self._hasNonPareto(function.variableImplementation)]
    
    def exportAllImages(self, directory, resultNames=None):
        if resultNames is None:
            resultNames = self.resultNames
        for functionName in self.getFunctionNames():
            function = self.functions[functionName.lower()]
            filename = directory + "/" + function.functionName
            generation = [0] * len(resultNames)
            self.exportToImage(function, generation, True, resultNames, filename + "_fun.png")
            self.exportToImage(function, generation, False, resultNames, filename + "_var.png")
    
    def exportToImage(self, function, generation, functionSpace, resultNames, filename, latex=False):
        toPlot = self._getSolutionsToPlot(function, generation, functionSpace, resultNames)
        if functionSpace:
            if latex:
                axis = ["$f_1$", "$f_2$", "$f_3$"]
            else:
                axis = ["F1", "F2", "F3"]
        else:
            if latex:
                axis = ["$x_1$", "$x_2$", "$x_3$"]
            else:
                axis = ["x1", "x2", "x3"]
                
        functionName = Utils.getFunctionNameLatex(function.functionName) if latex else function.functionName
        if latex:
            for solution in toPlot:
                solution[0] = Utils.getResultNameLatex(solution[0])
        self.plotter.plotSolution(toPlot, functionName, None if functionSpace else "Parameter space", axis[0], axis[1], axis[2], filename)
      
    def _getSolutionsToPlot(self, problem, generation, functionSpace, resultNames):
        solutions = []
        k = 0
        if Analyzer.__PARETO__ in resultNames:
            resultNames.remove(Analyzer.__PARETO__)
            resultNames.insert(0, Analyzer.__PARETO__)
            
        for name in resultNames:
            k += 1
            if functionSpace:
                solution = problem.getFunctionSolution(name)
            else:
                solution = problem.getVariableSolution(name)
            if solution is not None:
                rgb = 3*[0]
                for p in xrange(3):
                    if k & (1 << p) > 0:
                        rgb[p] = 255
                points = solution.getSolutionPoints(generation[k-1])
                solutions.append([name, points, rgb])
            
        return solutions
            
    def _hasNonPareto(self, implementations):
        if len(implementations) > 1:
            return True
        if len(implementations) == 0:
            return False
        return Analyzer.__PARETO__ not in implementations.keys()
    
    def _scanDirectory(self, directory):
        if not os.path.exists(directory) or not os.path.isdir(directory):
            print >> sys.stderr, "Directory '%s' does not exist!" % directory
            return
        
        resultName = self.getResultName(directory)
        for filename in dircache.listdir(directory):
            filename = str(directory + "/" + filename)
#            fileType, _ = mimetypes.guess_type(filename)
            #if fileType is None or "text" not in fileType or not self.isSolutionFile(filename):
            if not Utils.isSolutionFile(filename):
                continue
            
            functionName = Utils.getFunctionName(filename)
            genPos = max(-1, functionName.rfind("."), functionName.rfind("-"), functionName.rfind("_"))
            generation = 1 << 30
            if genPos >= 0:
                try:
                    generation = int(functionName[genPos+1:])
                    functionName = functionName[:genPos]
                except:
                    pass
                
            fnId = functionName.lower()
            if fnId in self.functions:
                function = self.functions[fnId]
            else:
                function = MOSolution(functionName)
                self.functions[fnId] = function
                
            if Utils.isFunctionFile(filename):
                function.addFunctionSolution(resultName, filename, generation)
            else:
                function.addVariableSolution(resultName, filename, generation)
            
    def getFunctionResults(self, functionName, resultNames):
        function = self.getResultsForFunction(functionName)
        solutions = []
        for name in resultNames:
            if name.lower() != Analyzer.__PARETO__:
                result = function.getFunctionSolution(name)
                if result is not None:
                    solutions.append([name, [result.getSolutionPoints(idx) for idx in xrange(result.count())]])
                
        return solutions
    
    def getFunctionPareto(self, functionName):
        pareto = self.getResultsForFunction(functionName).getFunctionSolution(Analyzer.__PARETO__)
        if pareto is None:
            return None
        return pareto.getSolutionPoints(0)
    
    def getFormattedValue(self, data1, data2, best, decimalFormat="%.4f", bestFormat="\\textbf{%s}"):
        if data1 is None:
            return "---"
        
        if isinstance(data1, types.StringType):
            return data1
        
        value = decimalFormat % data1
        if data2 is not None:
            value += " / " + (decimalFormat % data2)
        if best:
            value = bestFormat % value
        return value
    
    def getCurrentBestResult(self):
        convIdx = len(self.metrics.labels) - 2
        distIdx = convIdx + 1
        convergence = self.metrics.metricMean[convIdx]
        distribution = self.metrics.metricMean[distIdx]
        best = 0
        for i in xrange(1, self.nResults - 1):
            if convergence[i] > convergence[best] + Utils.__EPS__:
                best = i
            elif abs(convergence[i] - convergence[best]) < Utils.__EPS__ and distribution[i] > distribution[best]:
                best = i
                
        return best
    
    def generateMetricImage(self, functionName, metricName, metricIdx, filename, latex=False):
        print "    Generating figure for metric %s in problem %s" % (metricName, functionName)
        results = []
        for i in xrange(self.nResults - 1):
            result = [self.resultNames[i], [self.metrics.metricMin[metricIdx][i], self.metrics.metricQ1[metricIdx][i], self.metrics.metricMean[metricIdx][i], \
                                       self.metrics.metricQ3[metricIdx][i], self.metrics.metricMax[metricIdx][i]], ""]
            results.append(result)
            
        fname = Utils.getFunctionNameLatex(functionName) if latex else functionName
        mname = Utils.getFunctionNameLatex(metricName) if latex else metricName
        self.plotter.plotIndicators(results, fname, "", "", mname, filename)
    
    def generateBestImage(self, functionName, result, filename, worst=False, latex=False):
        print "    Generating %s figure of %s for %s" % ("worst" if worst else "best", result, functionName)
        function = self.functions[functionName.lower()]
        resultNames = [Analyzer.__PARETO__, result]
        if result is None:
            resultNames = self.resultNames
        generation = [0] * len(resultNames)
        
        pareto = self.getFunctionPareto(functionName)
        factor = -1 if worst else 1
        for i in xrange(len(resultNames)):
            if resultNames[i] == Analyzer.__PARETO__:
                continue
            
            results = self.getFunctionResults(functionName, [resultNames[i]])
            bestValue = factor * (1 << 30)
            metrics = Metrics(pareto, [results[0][1]])
            for run in xrange(len(results[0][1])):
                metrics.setSolutionsToCompare(0, run, None, None)
                value = metrics.deltaP()
                if value*factor < bestValue*factor:
                    bestValue = value
                    generation[i] = run
        
        self.exportToImage(function, generation, True, resultNames, filename, latex)
        
    def computeMetrics(self, functionName):
        pareto = self.getFunctionPareto(functionName)
        results = self.getFunctionResults(functionName, self.resultNames)
        self.metrics.computeMetrics(pareto, results)
        