'''
Created on Dec 11, 2011

@author: Moises Osorio [WCoder]
'''

import math
import numpy
import os

__RESOURCES_DIR__ = os.path.dirname(__file__) + "/../resources/"
__EPS__ = 1e-6
__ROUND__ = 4
__RESULT_NAME_LATEX__ = {"moead": "MOEA/D", "paes": "PAES", "nsga2": "NSGA-II", "mocde": "pe-mocde", 
                           "mocde-L10": "ne-mocde$_{10}$", "mocde-L20": "ne-mocde$_{20}$", "mocde-L50": "ne-mocde$_{50}$"}
__METRIC_NAME_LATEX__ = {"Inverted Generational Distance": "I$_{IGD}$", "Delta P": "I$_{\Delta_p}$", "Spacing": "I$_S$", "Hypervolume": "I$_H$", 
                         "Coverage": "I$_C$", "Additive Epsilon": "I$_{\epsilon^+}$", "Multiplicative Epsilon": "I$_{\epsilon^*}$"}
__FUNCTION_NAME_LATEX__ = {}

def getResultNameLatex(name):
    if name in __RESULT_NAME_LATEX__:
        return __RESULT_NAME_LATEX__[name]
    return name
    
def getMetricNameLatex(name):
    if name in __METRIC_NAME_LATEX__:
        return __METRIC_NAME_LATEX__[name]
    return name
    
def getFunctionNameLatex(name):
    if name in __FUNCTION_NAME_LATEX__:
        return __FUNCTION_NAME_LATEX__[name]
    return name

def dominates(x, y):
    """
    Returns True if vector x dominates vector y. False otherwise.
    """
    counter = 0
    for i in xrange(len(x)):
        if x[i] > y[i]:
            return False
        if x[i] == y[i]:
            counter += 1
        
    return counter < len(x)
        
        
def weaklyDominates(x, y):
    """
    Returns True if vector x weakly dominates vector y. False otherwise.
    """
    for i in xrange(len(x)):
        if x[i] > y[i]:
            return False
        
    return True

def nearestNeighborDistance(x, i):    
    """
    Computes the distance to the nearest neighbor in the set of vectors x. Uses Hamming distance.
    """
    return min(numpy.linalg.norm(x[i] - x[j], 1) for j in xrange(len(x)) if i != j)

def readFile(filename):
    points = []
    f = open(filename, "r")
    for line in f:
        point = [float(x) for x in line.split()]
        if len(point) > 0:
            points.append(point)

    f.close()
    
    maxPoints = 10000 # FIXME: Hack to speed it up
    if len(points) > maxPoints:
        skip = int(math.ceil(len(points) / maxPoints))
        points = [points[i] for i in xrange(0, len(points), skip)]
    
    return points
    
def getFunctionName(filename):
    filename = filename[filename.rfind("/")+1:]
    if "." in filename:
        filename = filename[:filename.rfind(".")]
    return filename.lower().replace("_fun", "").replace("_var", "").replace("fun", "").replace("var", "")\
        .replace("front_", "").replace("pareto_", "").replace("pf_", "").replace("_pf", "").replace("_front", "")\
        .replace("_pareto", "").replace("front", "").replace("pareto", "").upper()

def isSolutionFile(filename):
    if not os.path.exists(filename) or os.path.isdir(filename):
        return False
    
    f = open(filename)
    try:
        tries = 5 # Try 5 times to check if the file is valid
        lastlen = -1
        for line in f:
            points = [float(x) for x in line.split()]
            if lastlen != -1 and len(points) != lastlen:
                return False
            
            lastlen = len(points)
            tries = tries - 1
            if tries == 0:
                break
            
        return lastlen >= 2
    except Exception:
        return False
    finally:
        f.close()
        
def isFunctionFile(filename):
    return "var" not in filename.lower()

def createListList(n):
    x = []
    for _ in xrange(n):
        x.append([])
    return x

def _extractFunction(f):
    idx = len(f)
    while idx > 0 and f[idx-1].isdigit():
        idx = idx - 1
    n = 0 if idx == len(f) else int(f[idx:])
    return [f[0:idx], n]

def functionSorter(a, b):
    af = _extractFunction(a)
    bf = _extractFunction(b)
    if af[0] != bf[0]:
        return cmp(af[0], bf[0])
    return af[1] - bf[1]

def functionMatches(desc, testName):
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
    