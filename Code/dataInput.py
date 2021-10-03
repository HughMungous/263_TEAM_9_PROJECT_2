"""script to contain data input"""

# from glob import glob
import numpy as np
import pandas as pd

from typing import Dict, List, Tuple


def readLocationGroups()->Dict[str, List[str]]:
    """returns the stores in their location groups"""
    fileAddress = "./Data/LocationGroups.csv"

    locationGroupData = pd.read_csv(fileAddress, sep=',')
    
    res = {}
    for column in locationGroupData.columns:
        temp = list(locationGroupData[column][:]) + [np.NaN]
        temp = temp[:temp.index(np.NaN)]
        temp = [store.replace('_', ' ') if '_' in store else store for store in temp ]
        res[column] = temp   
        
    return res

def readAverageDemands(roundUp: bool = False)->Tuple[List[str], Dict[str, Dict[str, int]]]:
    """Returns the list of all stores and the demands for all stores from monday to saturday"""
    fileAddress = "./Data/AverageDemands.csv"
    averageDemands = pd.read_csv(fileAddress, sep=',',index_col=0)

    stores = averageDemands.index
    if roundUp:
        res = {day: {store: np.ceil(averageDemands[day][store]) for store in stores} for day in averageDemands.columns}
    else:
        res = {day: {store: averageDemands[day][store] for store in stores} for day in averageDemands.columns}
    return stores, res
    
def readTravelDurations()->pd.DataFrame:
    """Returns the adjacency matrix for the stores with the values converted to hours"""
    fileAddress = "./Data/WoolworthsTravelDurations.csv"
    
    return pd.read_csv(fileAddress,sep=',',index_col=0).applymap(lambda x: x/3600)

if __name__=="__main__":
    groups = readLocationGroups()
    stores, demands = readAverageDemands(roundUp=True)
    durationAdjacencyMatrix = readTravelDurations()

    # print(demands)
    pass