'''
Created on Dec 11, 2011

@author: Moises Osorio [WCoder]
'''

import os

import numpy

def dominates(x, y):
    """
    Returns True if vector x dominates vector y. False otherwise.
    """
    counter = 0
    for i in xrange(x.size):
        if x[i] > y[i]:
            return False
        if x[i] == y[i]:
            counter += 1
        
    return counter < x.size
        
        
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
    return points
    
def getFunctionName(filename):
    filename = filename[filename.rfind("/")+1:]
    if "." in filename:
        filename = filename[:filename.rfind(".")]
    return filename.lower().replace("_fun", "").replace("_var", "").replace("fun", "").replace("var", "")\
        .replace("front_", "").replace("pareto_", "").replace("pf_", "").replace("_pf", "").replace("_front", "")\
        .replace("_pareto", "").replace("front", "").replace("pareto", "").title()

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
