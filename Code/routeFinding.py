"""
File for route creation algorithms.

currently no implementation.
"""
from dataclasses import dataclass
from typing import Dict, List
from random import randint, seed

@dataclass
class RouteFinder:
    """Will change just keeping the work localised for now"""
    nodes: Dict[int, int] # node: demand - might change this later 
    adjacencyMatrix: List[List[int]] # durations between nodes: [i][j] = duration i to j
    maxDemand: int = 26

    def generate(self, numbers: List[int], k: int):
        """
        Generates combinations of numbers C k, preserves order.
        """
        if k == 1: return [[num] for num in numbers]

        # looping through each number and generating combinations from itself 
        # and the following numbers (preserving order)
        ans = []
        for i in range(len(numbers)-k+1):
            for number in self.generate(numbers[i+1:],k-1):
                ans.append([numbers[i]] + number)

        return ans

    def findValidSubgraphs(self, maxNodes: int = 1):
        """
        Function to generate subgraphs for application of a TSP algorithm.

        Finds subgraphs of size(maxNodes) from the nodes in a graph.
        Performs recursive calls incrementing maxNodes until no viable subgraph
        exists.
        """
        ans = [subGraph for subGraph in self.generate(list(self.nodes.keys()), maxNodes) if sum(nodes[node] for node in subGraph) <= 26]
        if not ans: # checking whether any subGraphs passed the test
            return []
        return ans + self.findValidSubgraphs(maxNodes+1)

       

    def antColonyTSP(self, subGraph: List[int]):
        """
        Function to find the best circuit for some subgraph using the cheapest insertion method.

        ants:
            memory - will not visit the same city twice
            knowledge of distance to surrounding nodes
            If distance is the same, choose using pheremone concentration
            P_{ij}^{k} (probability for ant k to choose j from i) = ([t_{ij}]^{a} * [n_{ij}]^{b})/(sum([t_{is}]^{a} * [n_{is}]^{b} for s in ValidNodes))
            where: 
                t = pheremone intensity on route/arc
                a = pheremone intensity regulation parameter
                n = visibility of node j from i = 1/d where d is the distance between two nodes
                b = visibility strength parameter
        """
        pass




if __name__ == "__main__":
    seed(508) # keep the tests the same

    nodes = {i: randint(4, 15) for i in range(10)}
    # print(nodes)

    routeFinder = RouteFinder(nodes=nodes, adjacencyMatrix=[])
    subgraphs = routeFinder.findValidSubgraphs(1)
    # for g in subgraphs:
    #     print(f"nodes:{g}\t\t total demand:{sum(nodes[n] for n in g)}")
    pass