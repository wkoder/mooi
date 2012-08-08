#! /usr/bin/python
'''
Created on Feb 22, 2012

@author: Moises Osorio [WCoder]
'''
from LatexReporter import LatexReporter
from Analyzer import Analyzer

import argparse
import os
import time
from Utils import functionSorter, functionMatches

parser = argparse.ArgumentParser(description="Analyze Multi-Objective Optimization algorithm results against true Pareto fronts")
parser.add_argument("--results", "-r", metavar="RESULT", nargs="+", help="results directory of an algorithm")
parser.add_argument("--functions", "-f", metavar="FUNCTION", nargs="*", help="function to test")
parser.add_argument("--pareto", "-p", help="true Pareto front directory")
parser.add_argument("--report", "-R", help="target report directory")
parser.add_argument("--highlight", "-hl", nargs="?", help="result name to highlight")
parser.add_argument("--presentation", action='store_const', const=True, default=False, help="if the document to generate is a presentation")
args = parser.parse_args()

reportDir = args.report
if reportDir is None:
    reportDir = "presentation" if args.presentation else "report"
    reportDir += "-" + time.strftime("%Y%m%d-%H%M%S")

reporter = LatexReporter()
reporter.setResultDirectories(args.results)
pareto = args.pareto
if pareto is None:
    pareto = os.path.dirname(__file__) + "/../resources/" + Analyzer.__PARETO__
reporter.setPareto(pareto)
functions = []
for functionName in reporter.getFunctionNames():
    if len(args.functions) == 0 or True in [functionMatches(fn, functionName) for fn in args.functions]:
        functions.append(functionName)
functions.sort(cmp=functionSorter)

reporter.generateReport(reportDir, functions, args.highlight, args.presentation)
