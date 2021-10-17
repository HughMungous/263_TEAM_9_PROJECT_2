'''
Mixed-integer linear pogram which solves for the most optimal solution

Parameters
---------


Returns
-------
routesChosen: np.array
              Array of lowest-cost routes

Notes
-----
This linear program uses the PuLP package in Python

'''


import numpy as np
import pandas as pd
from pulp import *

from typing import List



def findBestPartition(day: str, region: str, routes: List[List[str]], stores: List[str], durations: List[float], maxTrucks: int = 60, disp: bool = False):
    cost = lambda x: 225*x + 50 * max(0,x-4)
        
    # variable for whether a route is chosen 
    possibleRoutes = [LpVariable(region+f"_route_{i}", 0, 1, LpInteger) for i in range(len(routes))]
    
    # The variable 'routing_model' to contain the problem data where the objective is to minimise
    routing_model = pulp.LpProblem(f"{day}_{region}_RoutingModel", LpMinimize)

    # Objective Function is added to 'routing_model'
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

    # The routing_model is solved using PULP_CBC_CMD
    routing_model.solve(PULP_CBC_CMD(msg=disp))

    # Initialising the array routesChosen
    routesChosen = []
    
    # Iterating through the routes
    for i in range(len(routes)):
        if possibleRoutes[i].value() == 1.0:
            
            routesChosen.append(routes[i])
            
    # The routes chosen and status of the solution is returned
    return routesChosen, LpStatus[routing_model.status] == "Optimal"
