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



    