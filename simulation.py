"""
--
"""
from Code import dataInput

import pandas as pd
from scipy import stats
from numpy.random import seed

# plotting
from matplotlib import pyplot as plt

affirm = lambda x: x in "yY"

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


def sampleDurations(mean: float, std: float):
    # returns 1000 samples from a normal distribution 
    
    taskTime = stats.norm.rvs(loc=mean, scale=std, size=1000)
    
    return taskTime

def generateDemands():
    simDemands = {shop: [] for shop in averageDemands.index}
    
    for shop in averageDemands.index:
        simDemands[shop] = sampleDurations(*list(averageDemands.loc[shop,["Demand", "std"]]))
        
    return simDemands


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


def calculateDuration(demands, route, multiplier = 1):
    ans = 0
    for i in range(len(route)-1):
        ans += travelDurations[route[i]][route[i+1]]*multiplier
        ans += 0.125*demands[route[i+1]]
    return ans + travelDurations[route[-1]][depot]*multiplier

if __name__=="__main__":
    seed(508)
    # if affirm(input("Specify a seed? [Y/N]: ")):
        # seed(int(input("Please enter a seed: ")))

    cost = lambda x: 225*x + 50*max(0,x-4)
    
    demands = pd.DataFrame.from_dict(generateDemands(), orient='index')
    results = []
    lens, durations, rRoutes = [], [], []
    
    for i in range(1000):
        multiplier = stats.norm.rvs(loc=1.564,scale=0.10)
        curCost = 0
        curDur = 0

        tempRoutes = checkRoute(demands.loc[:,i])

        lens.append(len(tempRoutes))
        # rRoutes.append(tempRoutes)
        for route in tempRoutes:
            tempDuration = calculateDuration(demands.loc[:,i], route, multiplier=multiplier)
            curDur += tempDuration
            curCost += cost(tempDuration)

        assert(checkSolutionIsPartition(tempRoutes))
        results.append(curCost)
        durations.append(curDur/lens[-1])
    # dataInput.storeRoutes(results, 'Simulations/noDurationVariation.json')
    # rRoutes = [x for _,x in sorted(zip(results,rRoutes))]
    # print(f"Lower interval: {results[25]}, upper interval: {results[974]}")
    # dataInput.storeRoutes({"lower": rRoutes[25], "upper": rRoutes[975]}, "Simulations/confintRoutes.json")
    results.sort()
    durations.sort()
    # plt.show()
    # print(durations)
    
    pltCosts = True
    if pltCosts:
        plt.hist(results, density = True, histtype="stepfilled", alpha=0.2)
        plt.title("Histogram of costs in $ ...")
        print(f"Mean cost: {sum(results)/1000:.3f}, Lower CI: {results[25]:.3f}, Upper CI: {results[975]:.3f}")
        plt.show()

    pltDurations = True
    if pltDurations:
        plt.hist(durations, density=True, histtype='stepfilled', alpha=0.2)
        plt.title("Histogram of average durations")
        print(f"Mean duration: {sum(durations)/1000}, Lower CI: {durations[25]}, Upper CI: {durations[975]}")
        plt.show()