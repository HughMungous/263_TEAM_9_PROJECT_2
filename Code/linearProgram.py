
import numpy as np
import pandas as pd # We will discuss this more next week!
from pulp import *

from typing import List



def findBestPartition(day: str, region: str, routes: List[List[str]], stores: List[str], durations: List[float], maxTrucks: int = 60, disp: bool = False):
    cost = lambda x: 225*x + 50 * max(0,x-4)
        
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

    routing_model.solve(PULP_CBC_CMD(msg=disp))

    routesChosen = []
    if disp: 
        print("The choosen routes are out of a total of %s:" % len(possibleRoutes))
    for i in range(len(routes)):
        if possibleRoutes[i].value() == 1.0:
            if disp:
                print(routes[i])
            routesChosen.append(routes[i])

    return routesChosen, LpStatus[routing_model.status] == "Optimal"