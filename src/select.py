#! /usr/bin/python
'''
Created on Apr 10, 2012

@author: Moises Osorio
'''

from Analyzer import Analyzer
import Utils
import argparse
import dircache
import os
import shutil
import time

parser = argparse.ArgumentParser(description="Analyze Multi-Objective Optimization algorithm results against true Pareto fronts")
parser.add_argument("--name", "-n", help="name of the selected results")
parser.add_argument("--results", "-r", metavar="RESULT", nargs="+", help="results directory of an algorithm")
parser.add_argument("--functions", "-f", metavar="FUNCTION", nargs="*", help="function to test")
parser.add_argument("--pareto", "-p", help="true Pareto front directory")
args = parser.parse_args()

analyzer = Analyzer()
analyzer.setResultDirectories(args.results)
pareto = args.pareto
if pareto is None:
    pareto = os.path.dirname(__file__) + "/../resources/" + Analyzer.__PARETO__
analyzer.setPareto(pareto)
functions = []
for functionName in analyzer.getFunctionNames():
    if len(args.functions) == 0 or True in [analyzer.functionMatches(fn, functionName) for fn in args.functions]:
        functions.append(functionName.lower())
functions.sort()

resultDir = args.name
if resultDir[-1] == "/":
    resultDir = resultDir[:-1];
if os.path.exists(resultDir):
    newResultDir = "%s-%s" % (resultDir, time.strftime("%Y%m%d-%H%M%S"))
    print "Backing up previous report at '%s' to '%s'" % (resultDir, newResultDir)
    shutil.move(resultDir, newResultDir)

os.mkdir(resultDir)
for functionName in functions:
    print "Selecting best result for %s" % functionName
    analyzer.computeMetrics(functionName)
    bestIdx = analyzer.getCurrentBestResult()
    bestName = analyzer.resultNames[bestIdx]
    bestDir = analyzer.resultDirectories[bestIdx]
    print "    The best is %s" % bestName
    
    filesCopied = 0
    for filename in dircache.listdir(bestDir):
        filename = str(bestDir + "/" + filename)
        if not Utils.isSolutionFile(filename) or not Utils.isFunctionFile(filename):
            continue
        
        fnId = Utils.getFunctionName(filename).lower()
        genPos = max(-1, fnId.rfind("."), fnId.rfind("-"), fnId.rfind("_"))
        if genPos >= 0:
            fnId = fnId[:genPos]
        if fnId == functionName:
#            print "        Copying file '%s' to '%s'" % (filename, resultDir)
            filesCopied += 1
            shutil.copy(filename, resultDir)
            
    print "    Copied %d files!" % filesCopied
    