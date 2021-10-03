
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

# global variables: dont edit please 🙏
depot = "Distribution Centre Auckland"
locations = dataInput.readLocationGroups()
stores, demands = dataInput.readAverageDemands()
travelDurations = dataInput.readTravelDurations()
coordinates = dataInput.readStoreCoordinates()

routeFinder = routing.Pathfinder(travelDurations)

def generateRoutes(day: str, region: str, nPartitions:int=5):
    """generates the TSP routes/partitions for a given day and region """
    # getting the specific demands for the day and region
    regionalDemands = {location: demands[day][location] for location in locations['region']}
        
    regionRoutingObj = routing.Region(nodes=regionalDemands, locations=coordinates)

    validSubgraphs = regionRoutingObj.findValidSubgraphs()
    partitions = regionRoutingObj.createPartitions(validSubgraphs, nPartitions)
    
    routes = []
    for partition in partitions:
        temp = []
        for subgraph in partition:
            solution = routeFinder.nearestNeighbour([depot] + subgraph)
            # rearranging so the depot is always the start
            temp.append(solution[solution.index(depot):] + solution[:solution.index(depot)])
        routes.append(temp)

    return routes
    

def main():
    """
    This function will handle calling the other functions as well as plotting.
    """
    pass

if __name__ == "__main__":
    routes = generateRoutes('Monday', 'North')

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


