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
cost = lambda x: 225*x + 50*max(0,x-4)

depot = "Distribution Centre Auckland"
depotSet = set([depot])

travelDurations = dataInput.readTravelDurations()

weekdayDemands = dataInput.readDataWithStats()
saturdayDemands = dataInput.readSaturdayWithStats()

weekdayRoutes = dataInput.readRoutes("nonPartitionedSolutions/WeekdayAvg.json")
saturdayRoutes = dataInput.readRoutes("nonPartitionedSolutions/Saturday.json")

t1, t2 = [], []
for region in weekdayRoutes:
    t1.extend(weekdayRoutes[region])
    t2.extend(saturdayRoutes[region])
weekdayRoutes, saturdayRoutes = t1, t2

def checkSolutionIsPartition(routes, day = "WeekDayAvg"):
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

    if day == "WeekdayAvg":
        if rSet != set([loc for loc in weekdayDemands.index]) ^ depotSet:            
            print("Solution misses certain stores")
            print(f"Missing stores: {set(weekdayDemands.index) ^ rSet ^ depotSet}")
            res = False
    else:
        if rSet != set([loc for loc in saturdayDemands.index]) ^ depotSet:            
            print("Solution misses certain stores")
            print(f"Missing stores: {set(saturdayDemands.index) ^ rSet ^ depotSet}")
            res = False

    return res


def sampleDemandsWeekday(mean: float, std: float):
    # returns 1000 samples from a normal distribution 
    
    taskTime = stats.norm.rvs(loc=mean, scale=std, size=1000)
    return taskTime

def sampleDemandsSaturday(minx: float, maxx: float):
    # returns 1000 samples from a normal distribution 
    
    taskTime = stats.uniform.rvs(loc=minx, scale=maxx-minx, size=1000)
    return taskTime

def generateDemandsWeekday():
    simDemands = {shop: [] for shop in weekdayDemands.index}
    
    for shop in weekdayDemands.index:
        simDemands[shop] = sampleDemandsWeekday(*list(weekdayDemands.loc[shop,["Demand", "std"]]))
        
    return simDemands

def generateDemandsSaturday():
    simDemands = {shop: [] for shop in saturdayDemands.index}
    
    for shop in saturdayDemands.index:
        simDemands[shop] = sampleDemandsSaturday(*list(saturdayDemands.loc[shop,["min", "max"]]))
        
    return simDemands

def checkRoute(demands, routes):
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

def simulateWeekdays(scale = 0.1):
    demands = pd.DataFrame.from_dict(generateDemandsWeekday(), orient='index')
    morningResults = []
    morningLens, morningDurations = [], []
    # rRoutes = []

    print("Running weekday 8-12")
    for i in range(1000):
        multiplier = stats.norm.rvs(loc=1.399,scale=scale)
        curCost = 0
        curDur = 0

        tempRoutes = checkRoute(demands.loc[:,i], routes=weekdayRoutes)

        morningLens.append(len(tempRoutes))
        # rRoutes.append(tempRoutes)
       
        for route in tempRoutes:
            tempDuration = calculateDuration(demands.loc[:,i], route, multiplier=multiplier)
            curDur += tempDuration
            curCost += cost(tempDuration)

        # assert(checkSolutionIsPartition(tempRoutes))
        morningResults.append(curCost)
        morningDurations.append(curDur/morningLens[-1])

    eveningResults = []
    eveningLens, eveningDurations = [], []


    print("Running weekday 2-6")
    for i in range(1000):
        multiplier = stats.norm.rvs(loc=1.564,scale=scale)
        curCost = 0
        curDur = 0

        tempRoutes = checkRoute(demands.loc[:,i], routes=weekdayRoutes)

        eveningLens.append(len(tempRoutes))
       
        for route in tempRoutes:
            tempDuration = calculateDuration(demands.loc[:,i], route, multiplier=multiplier)
            curDur += tempDuration
            curCost += cost(tempDuration)

        # assert(checkSolutionIsPartition(tempRoutes))
        eveningResults.append(curCost)
        eveningDurations.append(curDur/eveningLens[-1])

    return morningResults, eveningResults, (morningDurations, eveningDurations)

def simulateSaturday(scale = 0.1):
    demands = pd.DataFrame.from_dict(generateDemandsSaturday(), orient='index')
    morningResults = []
    morningLens, morningDurations = [], []
    # rRoutes = []

    print("Running Saturday 8-12")
    for i in range(1000):
        multiplier = stats.norm.rvs(loc=1.208,scale=scale)
        curCost = 0
        curDur = 0

        tempRoutes = checkRoute(demands.loc[:,i], routes=saturdayRoutes)

        morningLens.append(len(tempRoutes))
        # rRoutes.append(tempRoutes)
       
        for route in tempRoutes:
            tempDuration = calculateDuration(demands.loc[:,i], route, multiplier=multiplier)
            curDur += tempDuration
            curCost += cost(tempDuration)

        # assert(checkSolutionIsPartition(tempRoutes), day="yes")
        morningResults.append(curCost)
        morningDurations.append(curDur/morningLens[-1])

    eveningResults = []
    eveningLens, eveningDurations = [], []

    print("Running Saturday 2-6")
    for i in range(1000):
        multiplier = stats.norm.rvs(loc=1.204,scale=scale)
        curCost = 0
        curDur = 0

        tempRoutes = checkRoute(demands.loc[:,i], routes=saturdayRoutes)

        eveningLens.append(len(tempRoutes))
       
        for route in tempRoutes:
            tempDuration = calculateDuration(demands.loc[:,i], route, multiplier=multiplier)
            curDur += tempDuration
            curCost += cost(tempDuration)

        # assert(checkSolutionIsPartition(tempRoutes), day="yes")
        eveningResults.append(curCost)
        eveningDurations.append(curDur/eveningLens[-1])

    return morningResults, eveningResults, (morningDurations, eveningDurations)

if __name__=="__main__":
    seed(508)
    # if affirm(input("Specify a seed? [Y/N]: ")):
        # seed(int(input("Please enter a seed: ")))

    weekdayMorn, weekdayEve, _ = simulateWeekdays()
    
    weekdayMorn.sort()
    weekdayEve.sort()
    
    pltWMorn = True
    if pltWMorn:
        plt.hist(weekdayMorn, density = False, histtype="stepfilled", alpha=0.2)
        plt.title("Distribution of Costs (Total) for Woolworths Weekday Inventory Routing during Morning Session (n = 1000)")
        plt.ylabel("Frequency")
        plt.xlabel("Cost, NZD")
        print(f"Mean cost: {sum(weekdayMorn)/1000:.3f}, Lower CI: {weekdayMorn[25]:.3f}, Upper CI: {weekdayMorn[975]:.3f}")
        plt.show()

    pltWEve = True
    if pltWEve:
        plt.hist(weekdayEve, density = False, histtype="stepfilled", alpha=0.2)
        plt.title("Distribution of Costs (Total) for Woolworths Weekday Inventory Routing during Afternoon Session (n = 1000)")
        plt.ylabel("Frequency")
        plt.xlabel("Cost, NZD")
        print(f"Mean cost: {sum(weekdayEve)/1000:.3f}, Lower CI: {weekdayEve[25]:.3f}, Upper CI: {weekdayEve[975]:.3f}")
        plt.show()

    saturdayMorn, saturdayEve, _ = simulateSaturday()
    
    saturdayMorn.sort()
    saturdayEve.sort()
    
    pltSMorn = True
    if pltSMorn:
        plt.hist(saturdayMorn, density = False, histtype="stepfilled", alpha=0.2)
        plt.title("Distribution of Costs (Total) for Woolworths Saturday Inventory Routing during Morning Session (n = 1000)")
        plt.ylabel("Frequency")
        plt.xlabel("Cost, NZD")
        print(f"Mean cost: {sum(saturdayMorn)/1000:.3f}, Lower CI: {saturdayMorn[25]:.3f}, Upper CI: {saturdayMorn[975]:.3f}")
        plt.show()

    pltWEve = True
    if pltWEve:
        plt.hist(saturdayEve, density = False, histtype="stepfilled", alpha=0.2)
        plt.title("Distribution of Costs (Total) for Woolworths Saturday Inventory Routing during Afternoon Session (n = 1000)")
        plt.ylabel("Frequency")
        plt.xlabel("Cost, NZD")
        print(f"Mean cost: {sum(saturdayEve)/1000:.3f}, Lower CI: {saturdayEve[25]:.3f}, Upper CI: {saturdayEve[975]:.3f}")
        plt.show()
