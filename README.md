# ENGSCI 263: Operations Research Project by Team 9
**Team members: Hugh Parsons, Emily Hacket Pain, Jacky Jin, Nicholas Lee**

The project objective is to find optimal routing plan to satisfy all Woolworth supermarket demands in Auckland, analyse the effect of uncertainty around the demand for pallets and traffic conditions, and finally analyse the effect of closing Woolworths supermarkets that are potentially redundant due to close proximity.

<p float="left">
  <img src="https://github.com/HughMungous/263_TEAM_9_PROJECT_2/blob/master/Visualisation/StoreLocations.png" width = 213>
  <img src="https://github.com/HughMungous/263_TEAM_9_PROJECT_2/blob/master/Visualisation/CostUncertainty.png" width=270>
  <img src="https://github.com/HughMungous/263_TEAM_9_PROJECT_2/blob/master/Visualisation/ShopClosureJustification.png" width=200>
</p>

This repository stores all the relevant files for our project.

## Installation 

The [requirements.txt](https://github.com/HughMungous/263_TEAM_9_PROJECT_2/blob/master/requirements.txt) file lists all Python libraries that our project code depend on, and they will be installed using:

```bash
pip install -r requirements.txt
```

Note that above installation of requirements.txt file is **not mandatory**. If your python packages are up-to-date, above step is unnecessary. 

## Files  

- ***mapping.ipynb*** - Jupyter notebook for route visualisation. 
- ***test.py*** - Testing suite to validate the solution outputs. 
- ***Data*** - Folder for given data in csv format. 
- ***Simulations*** - costs and 95% percentile interval of simulation results. 

## Results

**Optimal Routing plan (Weekday and Saturday, respectively):**
<p float="left">
  <img src="https://github.com/HughMungous/263_TEAM_9_PROJECT_2/blob/master/Visualisation/WeekdayOptimalRoute.png?raw=true" width =350>
  <img src="https://github.com/HughMungous/263_TEAM_9_PROJECT_2/blob/master/Visualisation/SaturdayOptimalRoute.png?raw=true" width=348>
</p>
