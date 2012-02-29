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
import shutil
import time
import types

class Analyzer:
    
    __PARETO__ = "pareto"
    __TEMPLATE_FILE__ = "report.tex"
    __TEMPLATE_DIR__ = Utils.__RESOURCES_DIR__ + "report/"
    __TEMPLATE_VAR__ = "%RESULTS%"

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
    
    def _getBlockLatex(self, name, description, data1, data2, best):
        n = len(data1)
        if description is None or (len(description) == 1 and description[0] is None):
            latex = ["            \\multicolumn{2}{|c||}{%s}" % name]
        else:
            latex = ["            \\multirow{%d}{*}{%s}" % (n, name)]
        for block in xrange(n):
            latexRow = []
            if description is not None and description[block] is not None:
                latexRow.append(description[block])
            for i in xrange(len(data1[block])):
                latexRow.append(self.getFormattedValue(data1[block][i], None if data2 is None \
                                                       else data2[block][i], best[block][i] if best is not None else False))
            latex.append("                & " + " & ".join(latexRow) + " \\\\")
        latex.append("                \\hline")
        return "\n".join(latex)
    
    def _getTableStartLatex(self, nColumns, big=True):
        latex = ["\\begin{table}"]
        latex.append("    \\tiny \\centering")
        sizeFactor = ""
        if big:
            latex.append("    \\begin{adjustwidth}{-3cm}{-3cm}")
            sizeFactor = "1.5"
        latex.append("        \\begin{tabularx}{%s\\textwidth}{| c | c || %s |}" % (sizeFactor, " | ".join(["K"] * nColumns)))
        latex.append("        \\hline")
        return "\n".join(latex)
    
    def _getTableEndLatex(self, caption, label, big=True):
        latex = ["        \\end{tabularx}"]
        if big:
            latex.append("    \\end{adjustwidth}")
        latex.append("    \\label{%s} \\caption{%s}" % (label, caption))
        latex.append("\\end{table}")
        return "\n".join(latex)
    
    def getCurrentLatex(self, functionName):
        nRows = len(self.metrics.labels)
        nColumns = self.nResults - 1
        
        latex = [self._getTableStartLatex(nColumns)]
        latex.append(self._getBlockLatex("Metric / Algorithm", None, [self.metrics.solutionNames], None, None))
        latex.append("            \\hline")
        row = 0
        while row < nRows:
            if row < self.metrics.nUnaryMetrics:
                toRow = row + 1
            elif row < nRows-2:
                toRow = row + nColumns
            else:
                toRow = nRows

            name = self.metrics.labels[row]
            if row == nRows - 2:
                latex.append("            \\hline")
                name = "\\textbf{%s}" % name
            latex.append(self._getBlockLatex(name, self.metrics.sublabels[row:toRow], self.metrics.metricMean[row:toRow], \
                                             self.metrics.metricStd[row:toRow], self.metrics.metricIsBest[row:toRow]))
            row = toRow
        
        latex.append(self._getTableEndLatex("Results for function %s." % functionName, "%s-results-table" % functionName))
        return "\n".join(latex)
    
    def _getFunctionLatex(self, functionName):
        pareto = self.getFunctionPareto(functionName)
        results = self.getFunctionResults(functionName, self.resultNames)
        self.metrics.computeMetrics(pareto, results)
        return self.getCurrentLatex(functionName)
    
    def _getBest(self, data):
        n = len(data)
        best = [False] * n
        maxValue = max(data)
        for i in xrange(n):
            if abs(maxValue - data[i]) < MetricsCalc.__EPS__:
                best[i] = True
                
        return best
    
    def _getAllSummaryLatex(self, functionNames, convPoints, distPoints, innerLatex):
        best = [self._getBest(convPoints), self._getBest(distPoints)]
        
        latex = [self._getTableStartLatex(len(self.metrics.solutionNames), False)]
        latex.append(self._getBlockLatex("Function / Algorithm", None, [self.metrics.solutionNames], None, None))
        latex.append("            \\hline")
        latex += innerLatex
        latex.append(self._getBlockLatex("\\textbf{Total}", ["Convergence", "Distribution"], [convPoints, distPoints], None, best))
        latex.append(self._getTableEndLatex("Result summary.", "results-summary-table", False))
        
        return "\n".join(latex)
    
    def generateReport(self, reportDir, functionNames):
        if reportDir[-1] != "/":
            reportDir += "/"
        if os.path.exists(reportDir):
            shutil.move(reportDir, "%s-%s" % (reportDir[:-1], time.strftime("%Y%m%d-%H%M%S")))
            
        shutil.copytree(Analyzer.__TEMPLATE_DIR__, reportDir)
        resultsLatex = self._getLatex(functionNames)
        
        template = open(Analyzer.__TEMPLATE_DIR__ + Analyzer.__TEMPLATE_FILE__, "r")
        report = open(reportDir + Analyzer.__TEMPLATE_FILE__, "w")
        for line in template:
            if line == Analyzer.__TEMPLATE_VAR__:
                report.write(resultsLatex)
            else:
                report.write(line)
    
        template.close()
        report.close()
    
    def _getLatex(self, functionNames):
        latex = ["\\newcolumntype{K}{>{\\centering\\arraybackslash$}X<{$}}"]
        innerSummaryLatex = []
        convPoints = [0] * (self.nResults - 1)
        distPoints = [0] * (self.nResults - 1)
        idx = 0
        for functionName in functionNames:
            latex.append(self._getFunctionLatex(functionName))
            idx += 1
            if idx % 7 == 0:
                latex.append("\\clearpage")
            latex.append("")
            innerSummaryLatex.append(self._getBlockLatex(functionName, ["Convergence", "Distribution"], \
                                                         [self.metrics.convPoints, self.metrics.distPoints], None, \
                                                         self.metrics.metricIsBest[-2:]))
            innerSummaryLatex.append("            \\hline")
            for i in xrange(self.nResults - 1):
                convPoints[i] += self.metrics.convPoints[i]
                distPoints[i] += self.metrics.distPoints[i]
        
        latex.append(self._getAllSummaryLatex(functionNames, convPoints, distPoints, innerSummaryLatex))
        return "\n".join(latex)
    