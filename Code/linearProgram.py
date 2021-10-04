
import numpy as np
import pandas as pd # We will discuss this more next week!
from pulp import *


def solve(day, partitions, durations, printResults = False):
    cost = lambda x: 225*x + 50*max(0,x-4)

    LpVars = {}
    for region in partitions:
        # creating a binary LpVariable to correspond with each partition
        LpVars[region] = [LpVariable(region+f"_partition_{i}", 0, 1, LpInteger) for i in range(len(partitions[region]))]


    # Inititating the problem
    prob = LpProblem("VehicleRoutingProblem_"+day, LpMinimize)

    # Objective funciton: the cost multiplied by where a partition is chosen
    # we cycle through each region, partition, and route in said partition
    prob += lpSum([cost(durations[region][i][j]) * LpVars[region][i] for region in partitions for i in range(len(LpVars[region])) for j in range(len(partitions[region][i]))]), "Total Cost from Trucking"

    # Constraints
    for region in partitions:
        # a partition must be selected for each region
        prob += lpSum(LpVars[region]) == 1, "Partition selected for " + region

    
    prob += lpSum(len(durations[region][i])*LpVars[region][i] for region in partitions for i in range(len(LpVars[region]))) <= 60, "Total number of trucks" # the total number of trucks must be less than or equal to 60 i dont know whether this needs to be fixed
    prob += lpSum([durations[region][i][j] * LpVars[region][i] / len(durations[region][i]) for region in partitions for i in range(len(LpVars[region])) for j in range(len(partitions[region][i]))]) / len(durations) <= 4, "Average Trip Duration" # the average route duration must be less than 4 hours
    

    


    # Solving routines - no need to modify
    prob.writeLP('Solutions/Trucking'+day+'.lp')

    prob.solve()
    
    if printResults:
        print("Status:", LpStatus[prob.status])

        # Each of the variables is printed with its resolved optimum value
        # for v in prob.variables():
            # print(v.name, "=", v.varValue)

        # The optimised objective function valof Ingredients pue is printed to the screen    
        print("Total Cost of Transportation = ", value(prob.objective))

    chosenPartitions = {}
    for region in partitions:
        for i in range(len(LpVars[region])):
            if LpVars[region][i].varValue >= 1: 
                chosenPartitions[region] = i
                break
    
    return value(prob.objective), chosenPartitions

if __name__ == "__main__":
    import dataInput, routing

    routes = dataInput.readRoutes('LPTEST/routes.json')
    durations = dataInput.readRoutes('LPTEST/durations.json')
    
    solve('Monday', routes, durations, True)