'''
Created on Aug 8, 2012

@author: Moises Osorio
'''
import shutil
import time
import os

from Analyzer import Analyzer
import Utils

class LatexReporter(object):
    
    __TEMPLATE_REPORT_FILE__ = "report.tex"
    __TEMPLATE_REPORT_DIR__ = Utils.__RESOURCES_DIR__ + "report/"
    __TEMPLATE_PRESENTATION_FILE__ = "presentation.tex"
    __TEMPLATE_PRESENTATION_DIR__ = Utils.__RESOURCES_DIR__ + "presentation/"
    __TEMPLATE_VAR__ = "%RESULTS%"

    def __init__(self):
        self.analyzer = Analyzer()
        
    def getFunctionNames(self, includeNotSolved=False):
        return self.analyzer.getFunctionNames(includeNotSolved)
    
    def setResultDirectories(self, results):
        self.analyzer.setResultDirectories(results)
        
    def setPareto(self, pareto):
        self.analyzer.setPareto(pareto)
    
    def _getBest(self, data):
        n = len(data)
        best = [False] * n
        maxValue = max(data)
        for i in xrange(n):
            if abs(maxValue - data[i]) < Utils.__EPS__:
                best[i] = True
                
        return best
    
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
                latexRow.append(self.analyzer.getFormattedValue(data1[block][i], None if data2 is None \
                                                       else data2[block][i], best[block][i] if best is not None else False))
            latex.append("                & " + " & ".join(latexRow) + " \\\\")
        latex.append("                \\hline")
        return "\n".join(latex)
    
    def _getTableStartLatex(self, nColumns, big, presentation):
        latex = []
        if presentation:
            latex.append("\\begin{frame}")
            latex.append("\\frametitle{\insertsubsection}")
            latex.append("\\vspace*{-0.2cm}")
            
        latex.append("\\begin{table}")
        latex.append("    \\tiny \\centering")
        sizeFactor = ""
        if big:
            if presentation:
                sizeFactor = "1.1"
                cmOff = "-0.5"
            else:
                sizeFactor = "1.5"
                cmOff = "-3"
            latex.append("    \\begin{adjustwidth}{%scm}{%scm}" % (cmOff, cmOff))
            
        latex.append("        \\begin{tabularx}{%s\\textwidth}{| c | c || %s |}" % (sizeFactor, " | ".join(["K"] * nColumns)))
        latex.append("        \\hline")
        
        return "\n".join(latex)
    
    def _getTableEndLatex(self, caption, label, big, presentation):
        latex = ["        \\end{tabularx}"]
        if big:
            latex.append("    \\end{adjustwidth}")
        if caption is not None and label is not None:
            latex.append("    \\caption{\\label{%s} %s}" % (label, caption))
        latex.append("\\end{table}")
        
        if presentation:
            latex.append("\\end{frame}")
        
        return "\n".join(latex)
    
    
    def getCurrentLatex(self, functionName, presentation):
        nRows = len(self.analyzer.metrics.labels)
        nColumns = self.analyzer.nResults - 1
        
        latex = [self._getTableStartLatex(nColumns, True, presentation)]
        latex.append(self._getBlockLatex("Metric / Algorithm", None, [self.analyzer.metrics.solutionNames], None, None))
        latex.append("            \\hline")
        row = 0
        while row < nRows:
            if row < self.analyzer.metrics.nUnaryMetrics:
                toRow = row + 1
            elif row < nRows-2:
                toRow = row + nColumns
            else:
                toRow = nRows

            name = self.analyzer.metrics.labels[row]
            if row == nRows - 2:
                latex.append("            \\hline")
                name = "\\textbf{%s}" % name
            latex.append(self._getBlockLatex(name, self.analyzer.metrics.sublabels[row:toRow], self.analyzer.metrics.metricMean[row:toRow], \
                                             self.analyzer.metrics.metricStd[row:toRow], self.analyzer.metrics.metricIsBest[row:toRow]))
            row = toRow
        
        latex.append(self._getTableEndLatex("Results for function %s." % functionName, \
                                            "%s-results-table" % functionName.lower(), True, presentation))
        return "\n".join(latex)
    
    def _getFigureLatex(self, filename, caption, presentation):
        latex = []
        if presentation:
            latex.append("\\begin{frame}")
            latex.append("\\frametitle{\insertsubsection}")
            latex.append("\\vspace*{-0.2cm}")

        latex.append("\\begin{figure}[!ht]")
        latex.append("\\centering")
        latex.append("\\includegraphics[width=\\textwidth]{%s}" % filename)
        latex.append("\\caption{%s}" % caption)
        latex.append("\\end{figure}")
        
        if presentation:
            latex.append("\\end{frame}")
        
        return "\n".join(latex)
    
    
    def _getFunctionLatex(self, functionName, reportDir, highlight, presentation):
        self.analyzer.computeMetrics(functionName)
        
        imageDir = reportDir + Analyzer.__IMAGES_DIR__
        if not os.path.exists(imageDir):
            os.makedirs(imageDir)
        
        desc = highlight
        if desc is None:
            desc = "all results"
        caption = "run of %s for %s (according to DeltaP)." % (desc, functionName)
        
        bestImage = Analyzer.__IMAGES_DIR__ + functionName + "_best_fun.png"
        self.analyzer.generateBestImage(functionName, highlight, reportDir + bestImage)
        latex = [self._getFigureLatex(bestImage, "Best %s" % caption, presentation)]
        
        worstImage = Analyzer.__IMAGES_DIR__ + functionName + "_worst_fun.png"
        self.analyzer.generateBestImage(functionName, highlight, reportDir + worstImage, True)
        latex.append(self._getFigureLatex(worstImage, "Worst %s" % caption, presentation))
        
        for i in xrange(len(self.analyzer.metrics.unaryMetricNames)):
            metricName = self.analyzer.metrics.unaryMetricNames[i]
            filename = Analyzer.__IMAGES_DIR__ + functionName + "_ind_" + metricName.replace(" ", "") + ".png"
            self.analyzer.generateMetricImage(functionName, metricName, i, reportDir + filename)
            latex.append(self._getFigureLatex(filename, "Indicador %s sobre el problema %s" % (metricName, functionName), presentation))
        
        latex.append(self.getCurrentLatex(functionName, presentation))
        return "\n".join(latex)
    
    
    def _getStartAllSummaryLatex(self, presentation):
        latex = [self._getTableStartLatex(len(self.analyzer.metrics.solutionNames), False, presentation)]
        latex.append(self._getBlockLatex("Function / Algorithm", None, [self.analyzer.metrics.solutionNames], None, None))
        latex.append("            \\hline")
        return latex
    
    def _getAllSummaryLatex(self, convPoints, distPoints, innerLatex, presentation, breakpoints):
        best = [self._getBest(convPoints), self._getBest(distPoints)]
        
        latex = self._getStartAllSummaryLatex(presentation)
        lastBreak = 0
        for breakpoint in breakpoints:
            latex += innerLatex[lastBreak:breakpoint]
            lastBreak = breakpoint
            latex.append(self._getTableEndLatex(None, None, False, presentation))
            latex += self._getStartAllSummaryLatex(presentation)
            
        latex += innerLatex[lastBreak:]
        latex.append(self._getBlockLatex("\\textbf{Total}", ["Convergence", "Distribution"], [convPoints, distPoints], None, best))
        latex.append(self._getTableEndLatex("Result summary.", "tab:results-summary", False, presentation))
        
        return "\n".join(latex)
    
    def generateReport(self, reportDir, functionNames, highlight, presentation):
        if reportDir[-1] != "/":
            reportDir += "/"
        if os.path.exists(reportDir):
            newResultDir = "%s-%s" % (reportDir[:-1], time.strftime("%Y%m%d-%H%M%S"))
            print "Backing up previous report at '%s' to '%s'" % (reportDir, newResultDir)
            shutil.move(reportDir, newResultDir)
            
        latexFile = LatexReporter.__TEMPLATE_PRESENTATION_FILE__ if presentation  \
            else LatexReporter.__TEMPLATE_REPORT_FILE__
        latexDir = LatexReporter.__TEMPLATE_PRESENTATION_DIR__ if presentation \
            else LatexReporter.__TEMPLATE_REPORT_DIR__

        print "Copying template files"
        shutil.copytree(latexDir, reportDir)
        print "Generating results latex"
        resultsLatex = self._getLatex(functionNames, reportDir, highlight, presentation)
        
        print "Adding results latex into report template"
        template = open(latexDir + latexFile, "r")
        report = open(reportDir + latexFile, "w")
        for line in template:
            if line.strip() == LatexReporter.__TEMPLATE_VAR__:
                report.write(resultsLatex)
            else:
                report.write(line)
    
        template.close()
        report.close()
        print "Report successfully generated!"
    
    def _getLatex(self, functionNames, reportDir, highlight, presentation):
        latex = []
        innerSummaryLatex = []
        convPoints = [0] * (self.analyzer.nResults - 1)
        distPoints = [0] * (self.analyzer.nResults - 1)
        idx = 0
        breakpoints = []
        for functionName in functionNames:
            idx += 1
            print "Generating results for function %s (%d/%d)" % (functionName, idx, len(functionNames))
            latex.append(self._getFunctionLatex(functionName, reportDir, highlight, presentation))
            if idx % 7 == 0 and not presentation:
                latex.append("\\clearpage")
            latex.append("")
            innerSummaryLatex.append(self._getBlockLatex(functionName, ["Convergence", "Distribution"], \
                                                         [self.analyzer.metrics.convPoints, self.analyzer.metrics.distPoints], None, \
                                                         self.analyzer.metrics.metricIsBest[-2:]))
            if presentation and idx % 14 == 0:
                breakpoints.append(len(innerSummaryLatex))
            else:
                innerSummaryLatex.append("            \\hline")
                
            for i in xrange(self.analyzer.nResults - 1):
                convPoints[i] += self.analyzer.metrics.convPoints[i]
                distPoints[i] += self.analyzer.metrics.distPoints[i]
        
        print "Generating all summary results"
        latex.append(self._getAllSummaryLatex(convPoints, distPoints, innerSummaryLatex, presentation, breakpoints))
        return "\n".join(latex)
    