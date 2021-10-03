"""
File for route creation algorithms.

currently no implementation.
"""
import pandas as pd

from dataclasses import dataclass
from typing import Dict, List, Any, Union
from random import randint, seed, sample, shuffle

@dataclass
class Region:
    """Will change just keeping the work localised for now"""
    nodes: Dict[str, Union[int, float]] # node: demand - might change this later 
    maxDemand: int = 26

    def generate(self, numbers: List[Any], k: int)->List[Any]:
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

    def findValidSubgraphs(self)->Dict[int, List[Any]]:
        """
        Function to generate subgraphs for application of a TSP algorithm.

        Finds subgraphs of size(maxNodes) from the nodes in a graph.
        Performs recursive calls incrementing maxNodes until no viable subgraph
        exists.
        """
        res = {}
        def subFunc(maxNodes: int):
            ans = [subGraph for subGraph in self.generate(list(self.nodes.keys()), maxNodes) if sum(self.nodes[node] for node in subGraph) <= 26]
            if not ans: # checking whether any subGraphs passed the test
                return []
            return ans 

        i = 1
        validAns = True
        while validAns:
            res[i] = subFunc(i)
            if not res[i]:
                del res[i]
                validAns = False
            i+=1
        
        return res         

    def createPartitions(self, subGraphs: Dict[int, List[Any]], maxNumber: int, randomSeed: int = 100, randomly: bool = False):
        """Function to generate partitions of the region provided the valid subgraphs
        
        Parameters:
            - havent decided on input typing yet
        """
        seed(randomSeed)
        storesSet, numStores = set(self.nodes.keys()), len(self.nodes.keys())

        ans = []
        while maxNumber:
            # choosing a random subgraph of random length to start with
            key = randint(1, len(subGraphs.keys()))
            current = [subGraphs[key][randint(0,len(subGraphs[key])-1)]]
            cSet = set(current[0]) # maintaining a set for set operations
            
            while storesSet - cSet: # while we have not found a partition
                # Going from the largest subGraps to the smallest
                if not randomly:
                    for i in range(min(numStores-len(cSet), max(subGraphs.keys())), 0, -1):
                        # randomly sorting the possible graphs
                        temp = sample(subGraphs[i], len(subGraphs[i]))
                        for j in range(len(temp)):
                            if cSet.isdisjoint(set(temp[j])):
                                cSet |= set(temp[j]) # updating the set
                                current.append(temp[j]) # updating the  current partition

                else:
                    randomisedKeys = list(range(1, min(numStores-len(cSet), max(subGraphs.keys()))+1))
                    shuffle(randomisedKeys)
                    for i in randomisedKeys:
                    
                        # randomly sorting the possible graphs
                        temp = sample(subGraphs[i], len(subGraphs[i]))
                        for j in range(len(temp)):
                            if cSet.isdisjoint(set(temp[j])):
                                cSet |= set(temp[j]) # updating the set
                                current.append(temp[j]) # updating the  current partition

            ans.append(current)

            maxNumber-=1
        
        return ans

@dataclass     
class Pathfinder:
    durations: pd.DataFrame
    # demands: Dict[str, Union[int, float]]
    def nearestNeighbour(self, graph: List[str], randomSeed: int = 100):
        seed(randomSeed)
        # selecting a random starting point
        
        visited = sample(graph, 1)

        unvisited = graph[:]
        unvisited.remove(visited[0])

        while unvisited:
            cMin = unvisited[0]
            for node in unvisited:
                if self.durations[visited[-1]][node] < self.durations[visited[-1]][cMin]:
                    cMin = node

            visited.append(cMin)
            unvisited.remove(cMin)
        return visited






from glob import glob
if __name__ == "__main__":
    seed(508) # keep the tests the same
    
    

    # nodes = {i: randint(4, 15) for i in range(10)}
    # print(nodes)

    # routeFinder = RouteFinder(nodes=nodes, adjacencyMatrix=[])
    # subgraphs = routeFinder.findValidSubgraphs(1)
    # print(subgraphs)
    # for g in subgraphs:
    #     print(f"nodes:{g}\t\t total demand:{sum(nodes[n] for n in g)}")
    pass