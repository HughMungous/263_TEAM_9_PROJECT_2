
## module imports
from Code import routing, dataInput

# data handling
import numpy as np
import pandas as pd
from glob import glob
# from collections import Counter

# plotting
# from matplotlib import pyplot as plt
# import seaborn as sns

# type handling
# from typing import List

"""
This file shoud contain tests.

try to format them as:
    test(FunctionBeingCalled)():

then add the tests to the main function.
"""

def main()->None:
    pass


if __name__ == "__main__":
    depot = "Distribution Centre Auckland"
    locations = dataInput.readLocationGroups()
    stores, demands = dataInput.readAverageDemands()
    travelDurations = dataInput.readTravelDurations()

    routeFinder = routing.Pathfinder(travelDurations)

    runSouth = True
    if runSouth:
        southDemands = {day: {location: demands[day][location] for location in locations['South']} for day in demands}
        
        southernRoutesMonday = routing.Region(nodes=southDemands['Monday'])
        validSubgraphs = southernRoutesMonday.findValidSubgraphs()
        partitions = southernRoutesMonday.createPartitions(validSubgraphs, 5, randomly=True)
        
        routes = []
        for partition in partitions:
            temp = []
            for subgraph in partition:
                solution = routeFinder.nearestNeighbour([depot] + subgraph)
                # rearranging so the depot is always the start
                temp.append(solution[solution.index(depot):] + solution[:solution.index(depot)])

            routes.append(temp)

        for route in routes:
            avg = 0
            for partition in route:
                totalTime = 0
                for i in range(len(partition)-1):
                    totalTime += travelDurations[partition[i]][partition[i+1]] + 0.125*southDemands['Monday'][partition[i+1]]
                    totalTime += travelDurations[partition[-1]][depot]
                # print(f"route:{partition},\t\t totalTime:{totalTime:.3f}")
                avg += totalTime
            print(f"Partition: {route}\nAverage duration for the partition: {avg/len(route):.3f}\nNum trucks: {len(route)}")

    runCentral = False
    if runCentral:
        southDemands = {day: {location: demands[day][location] for location in locations['West']} for day in demands}
        
        southernRoutesMonday = routing.Region(nodes=southDemands['Monday'])
        validSubgraphs = southernRoutesMonday.findValidSubgraphs()
        partitions = southernRoutesMonday.createPartitions(validSubgraphs, 8, randomly=True)
        
        routes = []
        for partition in partitions:
            temp = []
            for subgraph in partition:
                solution = routeFinder.nearestNeighbour([depot] + subgraph)
                # rearranging so the depot is always the start
                temp.append(solution[solution.index(depot):] + solution[:solution.index(depot)])

            routes.append(temp)

        for route in routes:
            avg = 0
            for partition in route:
                totalTime = 0
                for i in range(len(partition)-1):
                    totalTime += travelDurations[partition[i]][partition[i+1]] + 0.125*southDemands['Monday'][partition[i+1]]
                    totalTime += travelDurations[partition[-1]][depot]
                # print(f"route:{partition},\t\t totalTime:{totalTime:.3f}")
                avg += totalTime
            print(f"Partition: {route}\nAverage duration for the partition: {avg/len(route):.3f}\nNum trucks: {len(route)}")
    # main()
    pass