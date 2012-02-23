"""
Created on Oct 9, 2011

@author: Moises Osorio [WCoder]
"""

import Utils

class MOSolution:
    """
    Handles a set of functions to the same problem.
    """

    def __init__(self, functionName):
        """
        Creates a solution handler.
        """
        self.functionName = functionName
        self.functionImplementation = {}
        self.variableImplementation = {}
    
    def addFunctionSolution(self, solutionName, functionSolution, generation):
        solutionName = solutionName.lower()
        if solutionName not in self.functionImplementation:
            self.functionImplementation[solutionName] = MOImplementation();
        self.functionImplementation[solutionName].addImplementation(functionSolution, generation)
        
    def addVariableSolution(self, solutionName, variableSolution, generation):
        solutionName = solutionName.lower()
        if solutionName not in self.variableImplementation:
            self.variableImplementation[solutionName] = MOImplementation();
        self.variableImplementation[solutionName].addImplementation(variableSolution, generation)
        
    def getFunctionSolution(self, name):
        name = name.lower()
        if name not in self.functionImplementation.keys():
            return None
        return self.functionImplementation[name]
        
    def getVariableSolution(self, name):
        name = name.lower()
        if name not in self.variableImplementation.keys():
            return None
        return self.variableImplementation[name]
        
    def clear(self):
        for solution in self.functionImplementation.values():
            solution.clear()
        for solution in self.variableImplementation.values():
            solution.clear()
        
class MOImplementation:
    """
    History for one L{MOSolution}.
    """
    
    def __init__(self):
        self.functions = []
        
    def addImplementation(self, solution, generation):
        self.functions.append((generation, solution))
        self.functions.sort()
        
    def count(self):
        return len(self.functions)
    
    def getSolutions(self):
        solutions = []
        for _, solution in self.functions:
            solutions.append(solution)
        return solutions
    
    def getSolutionPoints(self, idx):
        _, solution = self.functions[idx % len(self.functions)]
        return Utils.readFile(solution)
    
    def clear(self):
        self.functions = []
        