#! /usr/bin/python
'''
Created on Feb 22, 2012

@author: Moises Osorio [WCoder]
'''
from Analyzer import Analyzer
import argparse
import os

parser = argparse.ArgumentParser(description="Analyze Multi-Objective Optimization algorithm results against true Pareto fronts")
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
        functions.append(functionName)
        
print analyzer.getLatex(functions)
