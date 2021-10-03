"""script to contain data input"""

# from glob import glob
import numpy as np
import pandas as pd

from typing import Dict, List, Tuple


def readLocationGroups(fileAddress: str = "./Data/LocationGroups.csv")->Dict[str, List[str]]:
    """returns the stores in their location groups"""
    

    locationGroupData = pd.read_csv(fileAddress, sep=',')
    
    res = {}
    for column in locationGroupData.columns:
        temp = list(locationGroupData[column][:]) + [np.NaN]
        temp = temp[:temp.index(np.NaN)]
        temp = [store.replace('_', ' ') if '_' in store else store for store in temp ]
        res[column] = temp   
        
    return res

def readAverageDemands(fileAddress: str = "./Data/AverageDemands.csv", roundUp: bool = False)->Tuple[List[str], Dict[str, Dict[str, int]]]:
    """Returns the list of all stores and the demands for all stores from monday to saturday"""
    
    averageDemands = pd.read_csv(fileAddress, sep=',',index_col=0)

    stores = averageDemands.index
    if roundUp:
        res = {day: {store: np.ceil(averageDemands[day][store]) for store in stores} for day in averageDemands.columns}
    else:
        res = {day: {store: averageDemands[day][store] for store in stores} for day in averageDemands.columns}
    return stores, res
    
def readTravelDurations(fileAddress: str = "./Data/WoolworthsTravelDurations.csv")->pd.DataFrame:
    """Returns the adjacency matrix for the stores with the values converted to hours"""
    
    return pd.read_csv(fileAddress,sep=',',index_col=0).applymap(lambda x: x/3600)

def readStoreCoordinates(fileAddress: str = "./Data/WoolworthsLocations.csv")->pd.DataFrame:
    """Read the longitude and latitude values from the WoolworthsLocations csv"""
    
    return pd.read_csv(fileAddress, sep=",",usecols=['Store','Lat','Long']).set_index('Store')
    
    

if __name__=="__main__":
    # groups = readLocationGroups()
    # stores, demands = readAverageDemands(roundUp=True)
    # durationAdjacencyMatrix = readTravelDurations()
    locations = readStoreCoordinates()
    print(locations.head())
    print(locations.columns)
    # print(demands)
    pass