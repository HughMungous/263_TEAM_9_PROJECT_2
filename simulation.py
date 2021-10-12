"""
--
"""
import pandas as pd
from scipy import stats

def alphaBetaFromAmB(a, m, b):
    # Taken from code by David L. Mueller
    #github dlmueller/PERT-Beta-Python
    first_numer_alpha = 2.0 * (b + 4 * m - 5 * a)
    first_numer_beta = 2.0 * (5 * b - 4 * m - a)
    first_denom = 3.0 * (b - a)
    second_numer = (m - a) * (b - m)
    second_denom = (b - a) ** 2
    second = (1 + 4 * (second_numer / second_denom))
    alpha = (first_numer_alpha / first_denom) * second
    beta = (first_numer_beta / first_denom) * second
    return alpha, beta

def generateTaskTime(a, m, b):
    # Taken from code by Kevin Jia
    # github??? 
    alpha, beta = alphaBetaFromAmB(a, m, b)
    location = a
    scale = b - a
    
    taskTime = stats.beta.rvs(alpha, beta) * scale + location
    
    return taskTime

def generateDemands(df: pd.DataFrame):
    simDemands = [] 
    for shop in df.index:
        simDemands.append(generateTaskTime(*list(df.loc[shop,["min","mode","max"]])))
        
    return simDemands
    

def simulateDurations():
    pass


def checkRoute(demands, routes):
    """needs to check demand and split the route if needed
    
    """
    #TODO: fix the depot variable
    depot = "dist..."
    newRoutes = []
    # going through each route and checking the demand
    for route in routes: 
        # cDemand stores the demand of the current "subroute", j the start of the subroute
        cDemand, j = 0, 1 
        tempRoutes = []
        for i in range(len(route[1:])):
            cDemand += demands[route[i]]
            if cDemand > 26:    # we split the route and start a new subroute
                tempRoutes.append([depot]+route[j:i])
                cDemand, j = demands[route[i]], i
        else: # adding on the remaining portion of the route 
            if route[j:i]:
                tempRoutes.append([depot]+route[j:i])

        newRoutes.extend(tempRoutes)
    return newRoutes

def runSimulation():
    """runs one iteration of the simulation - checks whether average duration is exceeded"""
    pass

def calculateDuration(demands, route, multiplier):
    ans = 0
    for i in range(len(route)-1):
        ans += travelDurations[route[i]][route[i+1]]*multiplier
        ans += 0.125*demands[route[i+1]]
    return ans + travelDurations[route[-1]][depot]

