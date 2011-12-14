"""
Created on Oct 9, 2011

@author: Moises Osorio [WCoder]
"""

import Utils

class MOSolution:
    """
    Handles a set of solutions to the same problem.
    """

    def __init__(self, functionName):
        """
        Creates a solution handler.
        """
        self.functionName = functionName
        self.functionImplementation = {}
        self.variableImplementation = {}
    
    def addFunctionSolution(self, solutionName, functionSolution, generation):
        if solutionName not in self.functionImplementation:
            self.functionImplementation[solutionName] = MOImplementation();
        self.functionImplementation[solutionName].addImplementation(functionSolution, generation)
        
    def addVariableSolution(self, solutionName, variableSolution, generation):
        if solutionName not in self.variableImplementation:
            self.variableImplementation[solutionName] = MOImplementation();
        self.variableImplementation[solutionName].addImplementation(variableSolution, generation)
        
    def getFunctionSolution(self, name):
        if name not in self.functionImplementation.keys():
            return None
        return self.functionImplementation[name]
        
    def getVariableSolution(self, name):
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
        self.solutions = []
        
    def addImplementation(self, solution, generation):
        self.solutions.append((generation, solution))
        self.solutions.sort()
        
    def count(self):
        return len(self.solutions)
    
    def getSolutions(self):
        solutions = []
        for _, solution in self.solutions:
            solutions.append(solution)
        return solutions
    
    def getSolutionPoints(self, idx):
        _, solution = self.solutions[idx]
        return Utils.readFile(solution)
    
    def clear(self):
        self.solutions = []
        