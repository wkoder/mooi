"""
Created on Oct 9, 2011

@author: Moises Osorio [WCoder]
"""

class MOSolution:
    """
    Handles a set of solutions to the same problem.
    """

    def __init__(self, functionName):
        """
        Creates a solution handler.
        """
        self.functionName = functionName
        self.functionPareto = None
        self.variablePareto = None
        self.functionSolution = MOSolutionHistory()
        self.variableSolution = MOSolutionHistory()
    
    def setFunctionPareto(self, functionPareto):
        self.functionPareto = functionPareto
        
    def setVariablePareto(self, variablePareto):
        self.variablePareto = variablePareto
        
    def addFunctionSolution(self, functionSolution, generation):
        self.functionSolution.addSolution(functionSolution, generation)
        
    def addVariableSolution(self, variableSolution, generation):
        self.variableSolution.addSolution(variableSolution, generation)
        
    def clear(self):
        self.functionSolution.clear()
        self.variableSolution.clear()
        
class MOSolutionHistory:
    """
    History for one L{MOSolution}.
    """
    
    def __init__(self):
        self.solutions = []
        
    def addSolution(self, solution, generation):
        self.solutions.append((generation, solution))
        
    def count(self):
        return len(self.solutions)
    
    def getSolutions(self):
        self.solutions.sort()
        solutions = []
        for _, solution in self.solutions:
            solutions.append(solution)
        return solutions
    
    def clear(self):
        self.solutions = []
        