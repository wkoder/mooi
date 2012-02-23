'''
Created on Feb 21, 2012

@author: Moises Osorio [WCoder]
'''
from MOSolution import MOSolution
from MetricsCalc import MetricsCalc
from ResultPlotter import ResultPlotter
import Utils
import dircache
import os

class Analyzer:
    
    __PARETO__ = "pareto"

    def __init__(self):
        self.plotter = ResultPlotter()
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
            self.exportToImage(function, 0, True, resultNames, filename + "_fun.png")
            self.exportToImage(function, 0, False, resultNames, filename + "_var.png")
    
    def exportToImage(self, function, generation, functionSpace, resultNames, filename):
        toPlot = self._getSolutionsToPlot(function, generation, functionSpace, resultNames)
        axis = ["x1", "x2", "x3"]
        if functionSpace:
            axis = ["F1", "F2", "F3"]
        self.plotter.plotSolution(toPlot, function.functionName, None if functionSpace else "Parameter space", axis[0], axis[1], axis[2], filename)
      
    def _getSolutionsToPlot(self, problem, generation, functionSpace, resultNames):
        solutions = []
        k = 0
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
                points = solution.getSolutionPoints(generation-1)
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
            
    def functionMatches(self, desc, testName):
        desc = desc.lower()
        testName = testName.lower()
        if desc == testName:
            return True
        if desc.endswith("*") and testName.startswith(desc[:-1]):
            return True
        try:
            testDim = None # FIXME: Get dimension?
            if desc.endswith("d") and testDim == int(desc[:-1]):
                return True
        except:
            None
        return False
    
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
    
    def _getLatexFunction(self, functionName):
        pareto = self.getFunctionPareto(functionName)
        results = self.getFunctionResults(functionName, self.resultNames)
        self.metrics.computeMetrics(pareto, results)
        return self.metrics.getLatex()
    
    def getLatex(self, functionNames):
        latex = []
        for functionName in functionNames:
            latex.append(self._getLatexFunction(functionName))
        
        return "\n".join(latex)
    