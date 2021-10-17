"""Main file to be run"""

## Imports
from Code import dataInput, routing, linearProgram

import pandas as pd
import numpy as np
from scipy import stats
from matplotlib import pyplot as plt

from typing import List, Dict, Tuple

#--------------------------------------------------------------------------------------------
#                                     Global Variables
#--------------------------------------------------------------------------------------------
settings = dataInput.readRoutes("settings.json") # global settings file

travelDurations = dataInput.readTravelDurations()
coordinates = dataInput.readStoreCoordinates()

depot = "Distribution Centre Auckland"
routeFinder = routing.Pathfinder(travelDurations)

#--------------------------------------------------------------------------------------------
#                                   Local Helper Functions
#--------------------------------------------------------------------------------------------

cost = lambda duration: 225*duration + 50*max(0, duration-4)

class LP_NOT_OPTIMAL(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

def calculateDuration(route: List[str], demands: Dict[str, float], multiplier: float = 1.0):
    """Calculates the duration for a route given the demands (durations are assumed to be global)"""
    ans = 0
    for i in range(len(route)-1):
        ans += travelDurations[route[i]][route[i+1]]*multiplier
        ans += 0.125*demands[route[i+1]]

    return ans + travelDurations[route[-1]][depot]*multiplier

#--------------------------------------------------------------------------------------------
#                                Initial Solution Generation
#--------------------------------------------------------------------------------------------

def getRoutes(regionalDemands: Dict[str, float], removeOutliers: float = 1, maxStops: int = 6):
    """Function to generate valid routes given the demands for a region on a specified day."""
        
    regionRoutingObj = routing.Region(nodes=regionalDemands, locations=coordinates)

    validSubgraphs = regionRoutingObj.findValidSubgraphs(removeOutliers=removeOutliers, maxStops=maxStops)
    
    routes = []
    for k in validSubgraphs:
        for route in validSubgraphs[k]:
            solution = routeFinder.nearestNeighbour([depot] + route)
            routes.append(solution[solution.index(depot):] + solution[:solution.index(depot)])

    return routes

def eliminatePoorRoutes(routes, demands, minLenToKeep: int = 2, maxDuration: float = 6.0):
    """Eliminates routes up to a certain length."""
    durations = [calculateDuration(route, demands) for route in routes] # ignore traffic multiplier

    newRoutes = [routes[i] for i in range(len(durations)) if durations[i] < maxDuration or len(routes[i]) <= minLenToKeep]
    return newRoutes

def findInitalSolution(day: str, demands: Dict[str, float], locations: Dict[str,List[str]], 
                       centroid_mean_ratio: float, max_stores: int, traffic_multiplier: float,
                       min_route_length: int, max_duration: float):
    """Finds the solutions for a given day..."""
    
    # demands = dataInput.readAverageDemands(roundUp=True)
    # locations = dataInput.readLocationGroups()

    
    solution = {}
    solutionStatus = True

    for region in ["North", "West", "Central","South"]:
        regionalDemands = {location: demands[day][location] for location in locations[region] if demands[day][location] > 0}

        routes = getRoutes(regionalDemands, removeOutliers=centroid_mean_ratio, maxStops=max_stores)
        routes = eliminatePoorRoutes(routes, regionalDemands, minLenToKeep=min_route_length, maxDuration=max_duration)
        stores = regionalDemands.keys()
        durations = [calculateDuration(route, regionalDemands, multiplier=traffic_multiplier) for route in routes]

        regionalSolution, problemStatus = linearProgram.findBestPartition(day, region, routes, stores, durations)
        
        solution[region] = regionalSolution
        solutionStatus = solutionStatus and problemStatus
        
    return solution, solutionStatus


## Traffic and demand simulations
#--------------------------------------------------------------------------------------------
#                               Traffic and Demand Simulations
#--------------------------------------------------------------------------------------------
def generateDemands(demands: pd.DataFrame, day: str, sampleSize: int=1000):
    simDemands = {shop: [] for shop in demands.index}
    
    for shop in demands.index:
        if day == "WeekdayAvg":
            simDemands[shop] = stats.norm.rvs(loc=demands["Demand"][shop], scale=demands["std"][shop], size=sampleSize)
        elif day == "Saturday":
            simDemands[shop] = stats.uniform.rvs(loc=demands["min"][shop],scale=demands["max"][shop] - demands["min"][shop], size=sampleSize)
        else:
            raise("Invalid day supplied")    
        
    return simDemands

def checkRoute(demands, routes):
    """
    needs to check demand and split the route if needed

    ...
    """
    newRoutes = []
    # going through each route and checking the demand
    for route in routes: 
        # cDemand stores the demand of the current "subroute", j the start of the subroute
        cDemand, j = 0, 1 
        tempRoutes = []
        for i in range(1,len(route)):
            cDemand += demands[route[i]]
            if cDemand > 26:    # we split the route and start a new subroute
                tempRoutes.append([depot]+route[j:i])
                cDemand, j = demands[route[i]], i
        else: # adding on the remaining portion of the route 
            if route[j:]:
                tempRoutes.append([depot]+route[j:])

        newRoutes.extend(tempRoutes)
    return newRoutes

def runSimulationInstance(demands: pd.DataFrame, routes: List[List[str]], trafficMultiplier: float, trafficStd: float = 0.1, simulationNumber: int = 1000):
    # demands = pd.DataFrame.from_dict(generateDemandsWeekday(), orient='index')
    newRoutes = []
    routeLengths = []
    routeDurations = []
    routeCosts = []

    # print("Running weekday 8-12")
    for i in range(simulationNumber):
        multiplier = stats.norm.rvs(loc=trafficMultiplier, scale=trafficStd)
        curCost = 0
        curDur = 0

        # splitting the routes to account for new demands 
        tempRoutes = checkRoute(demands.loc[:,i], routes=routes)

        routeLengths.append(len(tempRoutes))
        newRoutes.append(tempRoutes)
       
        for route in tempRoutes:
            tempDuration = calculateDuration(route, demands.loc[:,i], multiplier=multiplier)
            curDur += tempDuration
            curCost += cost(tempDuration)

        # assert(checkSolutionIsPartition(tempRoutes))
        routeCosts.append(curCost)
        routeDurations.append(curDur/routeLengths[-1])

    tempRoutes = [x for _, x in sorted(zip(routeDurations, newRoutes))]
    
    resRoutes = {
        "lower": tempRoutes[25],
        "median": tempRoutes[500],
        "upper": tempRoutes[975]
            }

    statistics = {
        "lengths": routeLengths, 
        "durations": routeDurations, 
        "costs": routeCosts
            }

    return resRoutes, statistics

## Store closure simulations
#--------------------------------------------------------------------------------------------
#                                 Store Closure Simulations
#--------------------------------------------------------------------------------------------

# nothing to see here...

## Main control functions
#--------------------------------------------------------------------------------------------
#                                   Main Control Functions
#--------------------------------------------------------------------------------------------

def initialOptimisation(days: List[str] = ["WeekdayAvg", "Saturday"]):
    localSettings = settings["inital_solution"]["run_args"]


    demands = dataInput.readAverageDemands(roundUp=localSettings["round_up"])
    locations = dataInput.readLocationGroups()

    solutions = {}
    for day in days:
        solutions[day] = []

        temp, solStatus = findInitalSolution(day, demands, locations, 
                                            centroid_mean_ratio=localSettings["centroid_mean_ratio"], 
                                            max_stores=localSettings["max_stores"][day], 
                                            traffic_multiplier=localSettings["traffic_multiplier"], 
                                            min_route_length=localSettings["min_route_length"], 
                                            max_duration=localSettings["max_duration"])
        
        if not solStatus:
            raise LP_NOT_OPTIMAL(f"\033[93mThe solution for {day} was not optimal\033[0m")

        for region in temp: # constructing a list of all routes for the day
            solutions[day].extend(temp[region])
    
    return solutions

def simulateUncertainty(initialSolutions: Dict[str, List[str]], days: List[str] = ["WeekdayAvg", "Saturday"], periods: List[str] = ["morning","evening"]):

    if any([day not in ["WeekdayAvg", "Saturday"] for day in days]): 
        raise("There is currently no implementation for days other than 'WeekdayAvg' and 'Saturday'.")

    localSettings = settings["uncertainty_simulation"]["run_args"]

    demands = {
        "WeekdayAvg": dataInput.readDataWithStats(roundUp=localSettings["round_up"]), 
        "Saturday": dataInput.readSaturdayWithStats(roundUp=localSettings["round_up"])
    }
    
    simulationResults = {}
    for day in days:
        dayDemands = generateDemands(demands[day], day)
        dayDemands = pd.DataFrame.from_dict(dayDemands, orient='index')

        dayResults = {}
        for i in range(len(periods)):
            newRoutes, statistics = runSimulationInstance(demands=dayDemands, routes=initialSolutions[day], 
                                                        trafficMultiplier=localSettings["traffic_multipliers"][day][i], 
                                                        trafficStd=localSettings["traffic_std"],
                                                        simulationNumber=localSettings["simulation_size"])
            
            periodResults = {}
            periodResults["routes"] = newRoutes
            periodResults["statistics"] = statistics
            
            dayResults[periods[i]] = periodResults

        simulationResults[day] = dayResults



    return simulationResults

def simulateStoreClosures(days: List[str] = ["WeekdayAvg", "Saturday"]):
    localSettings = settings["store_closures"]["run_args"]

    demands = dataInput.readDemandsWithStoreClosure(toClose=localSettings["stores_to_close_and_keep"], 
                                                    transferRatio=localSettings["transfer_ratio"],
                                                    roundUp=localSettings["round_up"])
    locations = dataInput.readLocationGroupsWithStoreClosure(toClose=localSettings["stores_to_close_and_keep"]) 
    
    solutions = {}
    for day in days:
        solutions[day] = []

        temp, solStatus = findInitalSolution(day, demands, locations, 
                                            centroid_mean_ratio=localSettings["centroid_mean_ratio"], 
                                            max_stores=localSettings["max_stores"][day], 
                                            traffic_multiplier=localSettings["traffic_multiplier"], 
                                            min_route_length=localSettings["min_route_length"], 
                                            max_duration=localSettings["max_duration"])
        
        if not solStatus:
            raise LP_NOT_OPTIMAL(f"\033[93mThe solution for {day} was not optimal\033[0m")

        for region in temp: # constructing a list of all routes for the day
            solutions[day].extend(temp[region])
    
    return solutions

#--------------------------------------------------------------------------------------------
#                                    Main Function
#--------------------------------------------------------------------------------------------

def main():
    np.random.seed(508)
    
    # initial solutions
    if settings["inital_solution"]["run"]:
        initialResults = initialOptimisation()
        
        if settings["inital_solution"]["save"]:
            dataInput.storeRoutes(initialResults, fileAddress="Solutions/initialRoutes.json")      
    else:
        initialResults = dataInput.readRoutes("Solutions/initialRoutes.json")

    # uncertainty simulations
    if settings["uncertainty_simulation"]["run"]:
        simulationResults = simulateUncertainty(initialSolutions=initialResults)

        if settings["uncertainty_simulation"]["save"]:
            dataInput.storeRoutes(simulationResults, fileAddress="Solutions/simulationResults.json") 
    else:
        simulationResults = dataInput.readRoutes("Solutions/simulationResults.json")

    # resolving with store closures
    if settings["store_closures"]["run"]:
        storeClosureResults = simulateStoreClosures()

        if settings["store_closures"]["save"]:
            dataInput.storeRoutes(storeClosureResults, fileAddress="Solutions/storeClosureSolutions.json") 
    else:
        simulationResults = dataInput.readRoutes("Solutions/storeClosureSolutions.json")


    return



if __name__ == "__main__":
    main()

