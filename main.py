
## module imports
from Code import routing, dataInput, linearProgram

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
stores, demands = dataInput.readAverageDemands(roundUp=True)
travelDurations = dataInput.readTravelDurations()
coordinates = dataInput.readStoreCoordinates()

routeFinder = routing.Pathfinder(travelDurations)

def generateRoutes(day: str, region: str, nPartitions:int=5, removeOutliers=0.5, maxStops=4):
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
    regionalDemands = {location: demands[day][location] for location in locations[region] if demands[day][location] != 0}
        
    regionRoutingObj = routing.Region(nodes=regionalDemands, locations=coordinates)

    validSubgraphs = regionRoutingObj.findValidSubgraphs(removeOutliers=removeOutliers, maxStops=maxStops)
    
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



def main(numRoutes: int):
    """
    This function will handle calling the other functions as well as plotting.
    """
    for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']:
        partitions, partitionDurations = {}, {}
        for region in ['North','West','Central','South']:
            partitions[region] = []
            partitionDurations[region] = []

            temporaryPartitions = generateRoutes(day, region, numRoutes, removeOutliers=1, maxStops=5)

            for partition in temporaryPartitions:
                tempRoutes = []
                tempDurations = []

                for route in partition:
                    tempRoutes.append(route)
                    tempDurations.append(calculateDuration(route, day))
                partitions[region].append(tempRoutes)
                partitionDurations[region].append(tempDurations)
        
        result, optimalParts = linearProgram.solve(day, partitions=partitions, durations=partitionDurations)
        
        print(f"Optimal solution for {day}: {result:.3f}")
        
        dataInput.storeRoutes({region: partitions[region][optimalParts[region]] for region in optimalParts}, f'Solutions/{day}Solution.json')


if __name__ == "__main__":
    numRoutes = int(input("Please enter the maximum number of partitions to be generated for each region:"))
    main(numRoutes=numRoutes)

    
    
    


