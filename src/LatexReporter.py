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
    __DATA_FORMAT__ = "%.4f"

    def __init__(self):
        self.analyzer = Analyzer("latex")
        
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
    
    def _getUnaryMetricLatex(self, data, functionNames):
        nm = self.analyzer.metrics.nUnaryMetrics
        nr = self.analyzer.nResults - 1
        nf = len(functionNames)
        nc = 2 + 4*nr

        latex = ["\\begin{sidewaystable}"]
        latex.append("    \\tiny \\centering")
        latex.append("    \\begin{tabularx}{\\textwidth}{| l | l |%s} \\hline" % (" K |" * 4*nr))
        
        header = "        \\multirow{2}{*}{Problema} & \\multirow{2}{*}{Indicador}"
        for resultName in self.analyzer.resultNames:
            if resultName != Analyzer.__PARETO__:
                header += " & \\multicolumn{4}{c|}{%s}" % Utils.getResultNameLatex(resultName)
        latex.append(header + " \\\\ \\cline{3-%d}" % (nc))
        latex.append((" & %s\\\\" % ("& \\mu & \\sigma & min & max " * nr)))
        
        for functionIdx in xrange(nf):
            latex.append("        \\hline \\hline \\multirow{%d}{*}{%s}" % (nm, Utils.getFunctionNameLatex(functionNames[functionIdx])))
            for metricIdx in xrange(nm):
                latex.append("            & %s" % (Utils.getMetricNameLatex(self.analyzer.metrics.unaryMetricNames[metricIdx])))
                best = [1 << 30] * 4
                factor = 1 if self.analyzer.metrics.unaryMetricOptType[metricIdx] == self.analyzer.metrics.__MIN__ else -1
                for i in [0, 2, 3]:
                    best[i] *= factor
                for resultIdx in xrange(nr):
                    for i in xrange(4):
                        f = 1 if i == 1 else factor
                        best[i] = min(best[i]*f, data[functionIdx][metricIdx][resultIdx][i]*f) * f
                for resultIdx in xrange(nr):
                    row = "                "
                    for i in xrange(4):
                        value = LatexReporter.__DATA_FORMAT__ % data[functionIdx][metricIdx][resultIdx][i]
                        if value == LatexReporter.__DATA_FORMAT__ % best[i]:
                            value = "\\textbf{%s}" % value
                        row += " & " + value
                    latex.append(row)
                latex.append("                \\\\%s" % ("" if metricIdx == nm-1 else " \\cline{2-%d}"%nc))
        latex.append("        \\hline")
        
        latex.append("    \\end{tabularx}")
        latex.append("    \\caption{\label{tab:-unary-results} Resultados para la familia de problemas .}")
        latex.append("\\end{sidewaystable}")
        return "\n".join(latex)
        
    def _getBinaryMetricLatex(self, data, functionNames):
        nm = self.analyzer.metrics.nBinaryMetrics
        nr = self.analyzer.nResults - 1
        nf = len(functionNames)
        nc = 3 + nr

        latex = ["\\begin{table}"]
        latex.append("    \\tiny \\centering")
        latex.append("    \\begin{tabularx}{\\textwidth}{| l | l | l |%s} \\hline" % (" K |" * nr))
        
        latex.append("        \\multirow{2}{*}{Problema} & \\multirow{2}{*}{Indicador} & \\multirow{2}{*}{Algoritmo A} & \\multicolumn{4}{c |}{Algoritmo B} " + \
                "\\\\ \\cline{4-%d}" % (nc))
        latex.append("                & & %s \\\\" % (" ".join("& %s" % Utils.getResultNameLatex(self.analyzer.resultNames[resultBIdx]).replace("$", "") for resultBIdx in xrange(nr))))
        
        for functionIdx in xrange(nf):
            latex.append("        \\hline \\hline \\multirow{%d}{*}{%s}" % (nm*nr, Utils.getFunctionNameLatex(functionNames[functionIdx])))
            for metricIdx in xrange(nm):
                factor = 1 if self.analyzer.metrics.binaryMetricOptType[metricIdx] == self.analyzer.metrics.__MIN__ else -1
                latex.append("            & \\multirow{%d}{*}{%s(A,B)}" % (nr, Utils.getMetricNameLatex(self.analyzer.metrics.binaryMetricNames[metricIdx])))
                for resultAIdx in xrange(nr):
                    row = "                %s & %s" % ("" if resultAIdx == 0 else "&", Utils.getResultNameLatex(self.analyzer.resultNames[resultAIdx]))
                    for resultBIdx in xrange(nr):
                        d = data[functionIdx][metricIdx][resultAIdx][resultBIdx]
                        if d is None:
                            value = "$---$"
                        else:
                            value = "%.4f" % d
                            if d*factor < data[functionIdx][metricIdx][resultBIdx][resultAIdx]*factor:
                                value = "\\textbf{%s}" % value
                        row += " & " + value
                    row += " \\\\ %s" % (("" if metricIdx == nm-1 else "\\cline{2-%d}" % nc) if resultAIdx == nr-1 else "\\cline{3-%d}" % nc)
                    latex.append(row)
                        
        latex.append("        \\hline")
        
        latex.append("    \\end{tabularx}")
        latex.append("    \\caption{\label{tab:-binary-results} Resultados para la familia de problemas .}")
        latex.append("\\end{table}")
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
        
        latex.append(self._getTableEndLatex("Resultados en el problema %s." % functionName, \
                                            "%s-results-table" % functionName.lower(), True, presentation))
        return "\n".join(latex)
    
    def _getFigureLatex(self, filename, caption, presentation):
        latex = []
        if presentation:
            latex.append("\\begin{frame}")
            latex.append("\\frametitle{\insertsubsection}")
            latex.append("\\vspace*{-0.2cm}")
        latex.append("\\begin{figure}[!ht]")
        latex.append("    \\centering")
        #latex.append("    \\includegraphics[width=\\textwidth]{%s}" % filename)
        latex.append("    \\resizebox{\\textwidth}{!}{\\input{%s}}" % filename)
        latex.append("    \\caption{%s}" % caption)
        latex.append("\\end{figure}")
        if presentation:
            latex.append("\\end{frame}")
        return "\n".join(latex)
    
    def _getCombinedFigureLatex(self, filename, caption):
        latex = []
        latex.append("        \\begin{center}")
        #latex.append("            \\includegraphics[width=\\textwidth]{%s}" % filename)
        #latex.append("            \\begin{adjustwidth}{-0.2\\textwidth}{}")
        #latex.append("            \\resizebox{1.4\\textwidth}{!}{\\input{%s}}" % filename)
        latex.append("            \\resizebox{\\textwidth}{!}{\\input{%s}}" % filename)
        #latex.append("            \\end{adjustwidth}")
        latex.append("            {%s}" % caption)
        latex.append("        \\end{center}")
        return "\n".join(latex)
    
    def _getFiguresLatex(self, filenames, captions, presentation, overallCaption=None):
        n = len(filenames)
        latex = []
        if presentation or n == 1:
            for i in xrange(n):
                latex.append(self._getFigureLatex(filenames[i], captions[i], presentation))
        else:
            latex.append("\\begin{figure}[!ht]")
            latex.append("    \\begin{center}")
            latex.append("    \\begin{minipage}{0.47\\textwidth}")
            for i in xrange(0, n, 2):
                latex.append(self._getCombinedFigureLatex(filenames[i], "(" + chr(ord("a") + i) + ") " + captions[i]))
            latex.append("    \\end{minipage}")
            latex.append("    \\hspace{5mm}")
            latex.append("    \\begin{minipage}{0.47\\textwidth}")
            for i in xrange(1, n, 2):
                latex.append(self._getCombinedFigureLatex(filenames[i], "(" + chr(ord("a") + i) + ") " + captions[i]))
            latex.append("    \\end{minipage}")
            latex.append("    \\end{center}")
            latex.append("    \\caption{%s}" % overallCaption)
            latex.append("\\end{figure}")
    
        return "\n".join(latex)
    
    def _getFunctionLatex(self, functionName, reportDir, highlight, presentation):
        self.analyzer.computeMetrics(functionName)
        
        imageDir = reportDir + Analyzer.__IMAGES_DIR__
        if not os.path.exists(imageDir):
            os.makedirs(imageDir)
        
        if highlight is None:
            desc = "todos los algoritmos"
        else:
            desc = Utils.getResultNameLatex(highlight)
        caption = "ejecuci\\'{o}n de %s al resolver el problema %s (de acuerdo a %s." % (desc, Utils.getFunctionNameLatex(functionName), \
                                                                                        Utils.getMetricNameLatex("Delta P"))
        
        latex = []
        if presentation:
            bestImage = Analyzer.__IMAGES_DIR__ + functionName + "_best_fun.tex"
            self.analyzer.generateBestImages(functionName, [highlight], [reportDir + ":" + bestImage], False, True)
            latex = [self._getFigureLatex(bestImage, "Mejor %s" % caption, presentation)]
            
            worstImage = Analyzer.__IMAGES_DIR__ + functionName + "_worst_fun.tex"
            self.analyzer.generateBestImages(functionName, [highlight], [reportDir + ":" + worstImage], True, True)
            latex.append(self._getFigureLatex(worstImage, "Peor %s" % caption, presentation))
        else:
            images = []
            captions = []
            bestImages = []
            resultNames = []
            for result in self.analyzer.resultNames:
                if result == Analyzer.__PARETO__:
                    continue
                bestImage = Analyzer.__IMAGES_DIR__ + functionName + "_" + result + "_best_fun.tex"
                resultNames.append(result)
                bestImages.append(reportDir + ":" + bestImage)
                images.append(bestImage)
                captions.append(Utils.getResultNameLatex(result))
            self.analyzer.generateBestImages(functionName, resultNames, bestImages, False, True)
            latex.append(self._getFiguresLatex(images, captions, presentation, "Mejor " + caption))
        
            images = []
            captions = []
            for i in xrange(len(self.analyzer.metrics.unaryMetricNames)):
                metricName = self.analyzer.metrics.unaryMetricNames[i]
                filename = Analyzer.__IMAGES_DIR__ + functionName + "_ind_" + metricName.replace(" ", "") + ".tex"
                self.analyzer.generateMetricImage(functionName, metricName, i, reportDir + ":" + filename, True)
                
                images.append(filename)
                captions.append("Indicador %s" % Utils.getMetricNameLatex(metricName))
            latex.append(self._getFiguresLatex(images, captions, presentation, "Indicadores en el problema %s" % Utils.getFunctionNameLatex(functionName)))
        
        #latex.append(self.getCurrentLatex(functionName, presentation))
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
    
    def _getLatex(self, functionNames, reportDir, highlight, presentation, showSummary=False):
        if showSummary:
            innerSummaryLatex = []
            convPoints = [0] * (self.analyzer.nResults - 1)
            distPoints = [0] * (self.analyzer.nResults - 1)
            breakpoints = []
        latex = []
        idx = 0
        unaryMetricTable = []
        binaryMetricTable = []
        ns = self.analyzer.nResults - 1
        for functionName in functionNames:
            idx += 1
            print "Generating results for function %s (%d/%d)" % (functionName, idx, len(functionNames))
            latex.append(self._getFunctionLatex(functionName, reportDir, highlight, presentation))
            if not presentation:
                latex.append("\\clearpage")
            latex.append("")
            
            if showSummary:
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
                    
            functionData = []
            for i in xrange(self.analyzer.metrics.nUnaryMetrics):
                metric = []
                for j in xrange(self.analyzer.metrics.nSolutions):
                    metric.append([self.analyzer.metrics.metricMean[i][j], self.analyzer.metrics.metricStd[i][j], self.analyzer.metrics.metricMin[i][j], \
                                   self.analyzer.metrics.metricMax[i][j]])
                functionData.append(metric)
            unaryMetricTable.append(functionData)
            functionData = []
            for i in xrange(self.analyzer.metrics.nBinaryMetrics):
                f = self.analyzer.metrics.nUnaryMetrics + i*ns
                metric = self.analyzer.metrics.metricMean[f:f+ns]
                functionData.append(metric)
            binaryMetricTable.append(functionData)
        
        latex.append(self._getUnaryMetricLatex(unaryMetricTable, functionNames))
        latex.append(self._getBinaryMetricLatex(binaryMetricTable, functionNames))
        
        if showSummary:
            print "Generating all summary results"
            latex.append(self._getAllSummaryLatex(convPoints, distPoints, innerSummaryLatex, presentation, breakpoints))
        return "\n".join(latex)
    