
import pandas as pd
import numpy as np
from pulp import *

from Code import dataInput, routing

## Data Input
# globalDay = 'Monday'
depot = "Distribution Centre Auckland"

locations       = dataInput.readLocationGroups()
stores, demands = dataInput.readAverageDemands(roundUp=True)
travelDurations = dataInput.readTravelDurations()
coordinates     = dataInput.readStoreCoordinates()

routeFinder = routing.Pathfinder(travelDurations)

cost = lambda x: 225*x + 50*max(0,x-4)

def calculateDuration(route):
    day = globalDay

    ans = 0
    for i in range(len(route)-1):
        ans += travelDurations[route[i]][route[i+1]]
        ans += 0.125*demands[day][route[i+1]]
    return ans + travelDurations[route[-1]][depot]

def getRoutes(day: str, region: str, removeOutliers: float = 0.4, maxStops: int = 4):
    # getting the specific demands for the day and region
    regionalDemands = {location: demands[day][location] for location in locations[region] if demands[day][location] != 0}
        
    regionRoutingObj = routing.Region(nodes=regionalDemands, locations=coordinates)

    validSubgraphs = regionRoutingObj.findValidSubgraphs(removeOutliers=removeOutliers, maxStops=maxStops)
    
    routes = []
    for k in validSubgraphs:
        for route in validSubgraphs[k]:
            solution = routeFinder.nearestNeighbour([depot] + route)
            routes.append(solution[solution.index(depot):] + solution[:solution.index(depot)])

    return routes

def eliminatePoorRoutes(routes, percentageToKeep: float = 0.5, minLenToKeep: int = 3):
    if percentageToKeep >= 1: return routes

    temp = {}
    for route in routes:
        if len(route) not in temp:
            temp[len(route)] = []
        temp[len(route)].append(route)
    
    ans = []
    for k in temp:
        if k > minLenToKeep:
            temp[k].sort(key=calculateDuration)
            temp[k] = temp[k][:int(len(temp[k])*percentageToKeep)]
        ans.extend(temp[k])
    
    return ans

def findBestPartition(day: str, region: str, routes, stores, durations, maxTrucks: int = 10):
    # variable for whether a route is chosen 
    possibleRoutes = [LpVariable(region+f"_route_{i}", 0, 1, LpInteger) for i in range(len(routes))]
    
    routing_model = pulp.LpProblem(f"{day}_{region}_RoutingModel", LpMinimize)

    # Objective Function
    routing_model += pulp.lpSum([cost(durations[i]) * possibleRoutes[i] for i in range(len(routes))])

    # specify the maximum number of tables
    routing_model += (
        pulp.lpSum(possibleRoutes) <= maxTrucks,
        "Maximum_number_of_trucks",
    )

    # A guest must seated at one and only one table
    for store in stores:
        routing_model += (
            # for each store, checks whether only one route satisfies it
            pulp.lpSum([possibleRoutes[i] for i in range(len(routes)) if store in routes[i]]) == 1,
            f"Must_supply_{store}",
        )

    routing_model.solve()

    routesChosen = []
    print("The choosen routes are out of a total of %s:" % len(possibleRoutes))
    for i in range(len(routes)):
        if possibleRoutes[i].value() == 1.0:
            print(routes[i])
            routesChosen.append(routes[i])

    return routesChosen

if __name__=="__main__":
    if input("Generate routes? (Y/N): ") in 'yY':
        for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']:
            # day = input("Which day would you like to model? ")
            globalDay = day

            solution = {}
            # region = input("Which region would you like to model? ")
            for region in ['North', 'West', 'South', 'Central']:
                routes = getRoutes(day, region, removeOutliers=0.5, maxStops=3)
                
                # toExclude = float(input("Which proportion of routes should be kept: [0-1]"))
                toExclude = 1.1
                northMonday = eliminatePoorRoutes(routes, toExclude)
                temp = findBestPartition(day, region, routes, [location for location in locations[region] if demands[day][location] != 0], [calculateDuration(route) for route in routes])
                solution[region] = temp

            if input("Save results? (Y/N) ") in 'yY':
                dataInput.storeRoutes(solution, f'nonPartitionedSolutions/{day}.json')

    elif input("Calculate solution values for saved solutions? (Y/N) ") in 'yY':
        verbose = False
        if input("Would you like a detailed output of the routes chosen? (Y/N) ") in 'yY':
            verbose = True

        day = input("Which day would you like to examine? ")
        globalDay = day

        totalCost, totalTrucks = 0,0

        
        print(f"Day: {day}")
        for region in ['North','West','Central','South']:
            temp = dataInput.readRoutes(f'nonPartitionedSolutions/{day}{region}.json')
            tempCost, tempTrucks = sum([cost(calculateDuration(route)) for route in temp]), len(temp)

            print(f"\n\nRegion: {region}")
            print(f"Number of trucks used: {tempTrucks}")
            print(f"Total cost: {tempCost:.3f}")

            if verbose:
                print("\n\t\tRoutes:\n\t\t------")
                for route in temp:
                    print(f"route: {route}, duration: {calculateDuration(route):.3f}, cost: {cost(calculateDuration(route)):.3f}")

            totalCost += tempCost
            totalTrucks += tempTrucks

        print(f"\n\nTotal cost for {day}: {totalCost:.3f}")
        print(f"Number of trucks for {day}: {totalTrucks}\n\n")