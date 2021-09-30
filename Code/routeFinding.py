"""
File for route creation algorithms.

currently no implementation.
"""
from dataclasses import dataclass

@dataclass
class regionRouteFinder:
    """Will change just keeping the work localised for now"""
    nodes: dict[int, int] # node: demand - might change this later 
    adjacencyMatrix: list[list[int]] # durations between nodes: [i][j] = duration i to j
    maxDemand: int = 26

    def generate(self, numbers, k):
        """
        Generates combinations of numbers C k, preserves order.
        """
        if k == 1: return [[num] for num in numbers]

        # looping through each number and generating combinations from itself 
        # and the following numbers (preserving order)
        ans = []
        for i in range(len(numbers)-k+1):
            for number in generate(numbers[i+1:],k-1):
                ans.append([numbers[i]] + number)

        return ans

    def generateSubgraphs(self, maxNodes):
        """
        Function to generate subgraphs for application of a TSP algorithm.

        Finds subgraphs of size(maxNodes) from the nodes in a graph.
        Performs recursive calls incrementing maxNodes until no viable subgraph
        exists.
        """
        ans = [subGraph for subGraph in self.generate(self.nodes.keys(), maxNodes) if sum(nodes[node] for node in subGraph) <= 26]
        if ans: # checking whether any subGraphs passed the test
            return ans + self.generateSubgraphs(maxNodes+1)
        return []

       

    def eulerianPathFinder(self, subGraph):
        """
        Function to find the best circuit for some subgraph.
        """
        pass