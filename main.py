
## module imports
from Code import routing, dataInput

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
    locations = dataInput.readLocationGroups()
    stores, demands = dataInput.readAverageDemands()
    travelDurations = dataInput.readTravelDurations()


    runSouth = True
    if runSouth:
        southDemands = {day: {location: demands[day][location] for location in locations['South']} for day in demands}
        
        southernRoutesMonday = routing.Region(nodes=southDemands['Monday'], adjacencyMatrix=travelDurations)
        print(southernRoutesMonday.findValidSubgraphs())
    # main()
    pass


