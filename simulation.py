"""
--
"""
from Code import dataInput

import pandas as pd
from scipy import stats
from matplotlib import pyplot as plt

depot = "Distribution Centre Auckland"
depotSet = set([depot])

travelDurations = dataInput.readTravelDurations()
averageDemands = dataInput.readDataWithStats()
routes = dataInput.readRoutes("nonPartitionedSolutions/WeekdayAvg.json")
temp = []
for region in routes:
    temp.extend(routes[region])
routes = temp[:]

def checkSolutionIsPartition(routes):
    """Function to check whether solution visits everystore"""

    res = True
    
    rSet = set()
    for route in routes:
        tempSet = set(route)
        if (rSet & tempSet) - depotSet:
            print("Solution visits same store twice")
            print(f"First overlapping store/s: {(rSet & tempSet) - depotSet}")
            res = False
        rSet |= tempSet

    if rSet != set([loc for loc in averageDemands.index]) ^ depotSet:            
        print("Solution misses certain stores")
        print(f"Missing stores: {set(averageDemands.index) ^ rSet ^ depotSet}")
        res = False

    return res

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
    
    taskTime = stats.beta.rvs(alpha, beta, size=1000) * scale + location
    
    return taskTime

def generateDemands():
    simDemands = {shop: [] for shop in averageDemands.index}
    
    
    for shop in averageDemands.index:
        simDemands[shop]= generateTaskTime(*list(averageDemands.loc[shop,["min","mode","max"]]))
        
    return simDemands
    

def simulateDurations():
    pass


def checkRoute(demands):
    """needs to check demand and split the route if needed
    
    """
    #TODO: fix the depot variable
    
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

def runSimulation():
    """runs one iteration of the simulation - checks whether average duration is exceeded"""
    pass

def calculateDuration(demands, route, multiplier = 1):
    ans = 0
    for i in range(len(route)-1):
        ans += travelDurations[route[i]][route[i+1]]*multiplier
        ans += 0.125*demands[route[i+1]]
    return ans + travelDurations[route[-1]][depot]

if __name__=="__main__":
    cost = lambda x: 225*x + 50*max(0,x-4)
    
    demands = pd.DataFrame.from_dict(generateDemands(), orient='index')
    results = []
    lens = []
    rRoutes = []
    for i in range(1000):
        curCost = 0
        tempRoutes = checkRoute(demands.loc[:,i])
        # lens.append(len(tempRoutes))
        rRoutes.append(tempRoutes)
        for route in tempRoutes:
            tempDuration = calculateDuration(demands.loc[:,i], route)
            curCost += cost(tempDuration)
        assert(checkSolutionIsPartition(tempRoutes))
        results.append(curCost)
    # dataInput.storeRoutes(results, 'Simulations/noDurationVariation.json')
    rRoutes = [x for _,x in sorted(zip(results,rRoutes))]
    print(f"Lower interval: {results[25]}, upper interval: {results[974]}")
    dataInput.storeRoutes({"lower": rRoutes[25], "upper": rRoutes[975]}, "Simulations/confintRoutes.json")
    # plt.hist(lens, density=True, histtype='stepfilled', alpha=0.2)
    # plt.show()