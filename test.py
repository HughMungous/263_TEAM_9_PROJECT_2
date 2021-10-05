
## module imports
from Code import routing, dataInput

# data handling
import numpy as np
import pandas as pd
from glob import glob
# from collections import Counter

# plotting
# from matplotlib import pyplot as plt
# import seaborn as sns

# type handling
# from typing import List

"""
This file shoud contain tests.
    Does it - No.... :()

try to format them as:
    test(FunctionBeingCalled)():

then add the tests to the main function.
"""
TEST_RESULT = lambda x: "\033[96mPASS\033[0m" if x else "\033[91mFAIL\033[0m"

def calculateDuration(route, day):
    ans = 0
    for i in range(len(route)-1):
        ans += travelDurations[route[i]][route[i+1]]
        ans += 0.125*demands[day][route[i+1]]
    return ans + travelDurations[route[-1]][depot]

def checkSolutionIsPartition(partitions, day):
    """Function to check whether solution visits everystore"""

    res = True
    for region in partitions:
        rSet = set()
        for route in partitions[region]:
            tempSet = set(route)
            if (rSet & tempSet) - depotSet:
                print("Solution visits same store twice")
                print(f"First overlapping store/s: {(rSet & tempSet) - depotSet}")
                res = False
            rSet |= tempSet

        if rSet != set([loc for loc in locations[region] if demands[day][loc] > 0.0]) ^ depotSet:            
            print("Solution misses certain stores")
            print(f"Missing stores: {set(locations[region]) ^ rSet ^ depotSet}")
            res = False

    return res

def checkAverageDuration(partitions, day):
    nTrucks, totDuration = 0, 0
    for region in partitions:
        nTrucks += len(partitions[region])
        totDuration += sum([calculateDuration(route, day) for route in partitions[region]])
    return totDuration / nTrucks <= 4

def checkNumberOfTrucks(partitions):
    return sum(len(partitions[region]) for region in partitions) <= 60

def verifySolutionValidity(partitions, day):
    print(f"\n\n\t\tTesting {day}:\n\t\t-------{'-'*len(day)}-\n")
    

    tests = {
        "Valid Partition Check": checkSolutionIsPartition(partitions, day),
        "Average Duration Check": checkAverageDuration(partitions, day),
        "Number of Trucks Check": checkNumberOfTrucks(partitions)
    }
    
    passed, numPassed = True, 0
    for test in tests:
        print(f"Result for [{test}]:\t{TEST_RESULT(tests[test])}")
        if not tests[test]: 
            passed = False
        else:
            numPassed += 1

    numSpaces = len(f"Result for [Average Duration Check]:") - len(f"{day} solution validity check:)")

    print(f"\n{day} solution validity check:{numSpaces*' '}\t{TEST_RESULT(passed)}")
    print(f"\nNumber of tests passed:\t\t\t{numPassed}\nNumber of tests failed:\t\t\t{len(tests) - numPassed}")
    
    return passed




def main()->None:
    pass


if __name__ == "__main__":
    depot = "Distribution Centre Auckland"
    depotSet = set([depot])

    locations = dataInput.readLocationGroups()
    stores, demands = dataInput.readAverageDemands()
    travelDurations = dataInput.readTravelDurations()
    coordinates = dataInput.readStoreCoordinates()

    routeFinder = routing.Pathfinder(travelDurations)

    statement ="TESTING PARTITION METHOD:"
    print(f"\t\t{statement}\n\t\t{'-'*len(statement)}")
    for testDay in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
        
        testPartitions = dataInput.readRoutes(f'Solutions/{testDay}Solution.json')
        verifySolutionValidity(testPartitions, testDay)
        
    statement ="TESTING LP METHOD:"
    print(f"\n\n\t\t{statement}\n\t\t{'-'*len(statement)}")
    for testDay in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
        testPartitions = dataInput.readRoutes(f'nonPartitionedSolutions/{testDay}.json')
        verifySolutionValidity(testPartitions, testDay)
    
