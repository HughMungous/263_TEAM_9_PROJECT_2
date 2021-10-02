
## module imports
from Code import routeFinding

# data handling
import numpy as np
import pandas as pd
from glob import glob
# from collections import Counter

# plotting
from matplotlib import pyplot as plt
# import seaborn as sns

# type handling
# from typing import List


def prims(graph, adjacencyMatrix, root):
    """incomplete"""
    for node in graph:
        node.distance = float('inf')
        node.predecessor = None
    root.distance = 0
    q = [node for node in graph]
    while q:
        u = min(q, key = lambda x: x.distance())
        for node in u.adjacents:
            if node in q and adjacencyMatrix[u][node] < node.distance:
                pass

def main():
    """
    This function will handle calling the other functions as well as plotting.
    """
    pass

if __name__ == "__main__":
    demands = glob("./Data/AverageDemands.csv")[0]

    runSouth = True
    if runSouth:
        south = ['Countdown Manukau', 'Countdown Manukau Mall',	'Countdown Manurewa', 'Countdown Papakura',	'Countdown Roselands', 'Countdown Takanini', 'SuperValue Flatbush', 'SuperValue Papakura']
        data = pd.read_csv(demands, delimiter=',',index_col=0)

        nodes = {store: data['Monday'][store] for store in south}

        # print(nodes)
        temp = routeFinding.RouteFinder(nodes=nodes, adjacencyMatrix=[])
        validRoutes = temp.findValidSubgraphs()
        
        validRoutesByLength = {i:[] for i in range(1,len(max(validRoutes, key = len))+1)}
        for route in validRoutes:
            validRoutesByLength[len(route)].append(route)

        # for i in validRoutesByLength:
            # print(f"i:{i}, routes:{validRoutesByLength[i]}")
        # print(len(validRoutes))
        pass
    # main()
    pass


