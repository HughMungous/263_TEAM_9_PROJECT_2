
import pandas as pd
import numpy as np
from pulp import *

from Code import dataInput, routing
from typing import List
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

def findBestPartition(day: str, region: str, routes: List[List[str]], stores: List[str], durations: List[float], maxTrucks: int = 60, disp = False):
    
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

    routing_model.solve(PULP_CBC_CMD(msg=0))

    routesChosen = []
    if disp: 
        print("The choosen routes are out of a total of %s:" % len(possibleRoutes))
    for i in range(len(routes)):
        if possibleRoutes[i].value() == 1.0:
            if disp:
                print(routes[i])
            routesChosen.append(routes[i])

    return routesChosen, LpStatus[routing_model.status] == "Optimal"

class LP_NOT_OPTIMAL(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

if __name__=="__main__":
    
    if input("Generate routes? (Y/N): ") in 'yY':
        autosave = input("Enable automatic saving? (Y/N) ") in 'yY'
        for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']:
            
            # day = input("Which day would you like to model? ")
            globalDay = day

            solution = {}
            # region = input("Which region would you like to model? ")
            solStatus = True
            for region in ['North', 'West', 'South', 'Central']:
                
                routes = getRoutes(day, region, removeOutliers=1, maxStops=5)
                
                # toExclude = float(input("Which proportion of routes should be kept: [0-1]"))
                # toExclude = 1.1
                # routes = eliminatePoorRoutes(routes, toExclude)
                temp, probStatus = findBestPartition(day, region, routes, [location for location in locations[region] if demands[day][location] != 0], [calculateDuration(route) for route in routes])
                solution[region] = temp
                solStatus = solStatus and probStatus

            if not solStatus:
                raise LP_NOT_OPTIMAL(f"\033[93mThe solution for {day} was not optimal\033[0m")
            if autosave:
                dataInput.storeRoutes(solution, f'nonPartitionedSolutions/{day}.json')
            elif input("Save results? (Y/N) ") in 'yY':
                dataInput.storeRoutes(solution, f'nonPartitionedSolutions/{day}.json')

    if input("Calculate solution values for saved solutions? (Y/N) ") in 'yY':
        if input("Would you like to examine a specific day? (Y/N) ") in 'yY':
            verbose = False
            if input("Would you like a detailed output of the routes chosen? (Y/N) ") in 'yY':
                verbose = True

            day = input("Which day would you like to examine? ")
            globalDay = day

            totalCost, totalTrucks = 0,0
            data = dataInput.readRoutes(f'nonPartitionedSolutions/{day}.json')

            print(f"Day: {day}")
            for region in ['North','West','Central','South']:
                
                tempCost, tempTrucks = sum([cost(calculateDuration(route)) for route in data[region]]), len(data[region])

                print(f"\n\nRegion: {region}")
                print(f"Number of trucks used: {tempTrucks}")
                print(f"Total cost: {tempCost:.3f}")

                if verbose:
                    print("\n\t\tRoutes:\n\t\t------")
                    for route in data[region]:
                        print(f"route: {route}, duration: {calculateDuration(route):.3f}, cost: {cost(calculateDuration(route)):.3f}")

                totalCost += tempCost
                totalTrucks += tempTrucks
        
        else:
            for day in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']:
                globalDay = day

                totalCost, totalTrucks = 0,0
                data = dataInput.readRoutes(f'nonPartitionedSolutions/{day}.json')

                print(f"\nDay: {day}")
                for region in ['North','West','Central','South']:

                    totalCost += sum([cost(calculateDuration(route)) for route in data[region]])
                    totalTrucks += len(data[region])

                print(f"\nTotal cost for {day}: {totalCost:.3f}")
                print(f"Number of trucks for {day}: {totalTrucks}\n")