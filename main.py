
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
    """generates the TSP routes/partitions for a given day and region 
    
    Parameter:
    ---------
    day: str
        The day of the week (Monday - Saturday)
    
    region: str
        The region (North, South, Central, West)

    nPartitions: Optional[int] = 5
        The number of partitions to be generated for the region
    """
    # getting the specific demands for the day and region
    regionalDemands = {location: demands[day][location] for location in locations[region]}
        
    regionRoutingObj = routing.Region(nodes=regionalDemands, locations=coordinates)

    validSubgraphs = regionRoutingObj.findValidSubgraphs(0.4)
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
    
def calculateDuration(route, day):
    ans = 0
    for i in range(len(route)-1):
        ans += travelDurations[route[i]][route[i+1]]
        ans += 0.125*demands[day][route[i+1]]
    return ans + travelDurations[route[-1]][depot]



def main():
    """
    This function will handle calling the other functions as well as plotting.
    """
    pass

if __name__ == "__main__":
    day = 'Monday'
    
    
    
    results = {}
    for region in ['North','West','Central','South']:
        results[region] = []

        partitions = generateRoutes(day, region)
        regionalDemands = {location: demands[day][location] for location in locations[region]}

        for partition in partitions:
            temp = []
            for route in partition:
                temp.append((route,calculateDuration(route, day)))
            results[region].append(temp)

    dataInput.storeRoutes(results)

    


