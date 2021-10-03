
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

try to format them as:
    test(FunctionBeingCalled)():

then add the tests to the main function.
"""

def main()->None:
    pass


if __name__ == "__main__":
    locations = dataInput.readLocationGroups()
    stores, demands = dataInput.readAverageDemands()
    travelDurations = dataInput.readTravelDurations()


    runSouth = True
    if runSouth:
        southDemands = {day: {location: demands[day][location] for location in locations['South']} for day in demands}
        
        southernRoutesMonday = routing.Region(nodes=southDemands['Monday'], adjacencyMatrix=travelDurations)
        validSubgraphs = southernRoutesMonday.findValidSubgraphs()
        
        for s in southernRoutesMonday.createPartitions(validSubgraphs, 5):
            print(s)

    # main()
    pass