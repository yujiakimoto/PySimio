# PySimio: A Library for Discrete-Event Simulation
**PySimio** is a Python library for object-oriented discrete-event simulation. You can simulate multiple agents (vehicles, entities) in a non-deterministic system. We support muilti-core processing to speed up experiments. 

![Animation](images/animation.gif)

## Features
- Object-Oriented Simulation
- Animation
- Commandline Debugging
- Statistic Collection and Data Visualization 
- Multicore Processing

## Setup
PySimio is built with the following libraries:
- `numpy` (back-end numerical calculations)  
- `pandas` (reading/writing data logs)  
- `seaborn, matplotlib` (data visualization)  
- `pygame` (animation rendering)   
  
All of the above packages can be installed through the package management system pip as below:
```
pip install numpy pandas seaborn matplotlib pygame
```
- `pysmac`  (Bayesian optimization) 
```
pip install git+https://github.com/sfalkner/pysmac.git --user
```

We highly recommend using **Python 3.6.1** or greater.
We also discovered the issue that pygame fails to render properly with Mac retina display ([link](https://stackoverflow.com/questions/29834292/pygame-simple-loop-runs-very-slowly-on-mac)).


## Sample Usage
We model several bus routes around Ithaca, NY to help the Tompkins Department of Going-Places (TDOG) save Cornell students from the perilous weather of upstate New York.  
![Route map](data/map.png)

### Model
```Python
# create BusStop objects  
depot = BusStop('TDOG Depot')  
weg_east = BusStop('Wegmans-Eastbound')  
weg_west = BusStop('Wegmans-Westbound')  
com_east = BusStop('Commons-Eastbound')  
com_west = BusStop('Commons-Westbound')  
ctown = BusStop('Collegetown')  
  
# route distance data  
r1d = [0.5, 2, 2, 2, 2, 0.5]  
r2d = [2, 2, 0.3]  
r3d = [0.5, 2, 0.3, 2, 0.5]    

# route switch point data - see Documentation for details
r1s = {2: {depot: [2.5,1], weg_east: [2,1], com_east: [0,1], ctown: [0,2], com_west: [5,1], weg_west: [3,1]},
       3: {depot: [0,1], weg_east: [0,2], com_east: [4,4], ctown: [2,4], com_west: [0,4], weg_west: [0,0]}}
r2s = {1: {com_east: [0,3], ctown: [0,4], com_west: [0,5]},
       3: {com_east: [0,3], ctown: [2,4], com_west: [0,4]}}
r3s = {1: {depot: [0,1], weg_east: [0,2], com_east: [0,3], com_west: [0,5], weg_west: [0,0]},
       2: {depot: [2.5,1], weg_east: [2,1], com_east: [0,1], com_west: [5,1], weg_west: [3,1]}}
   
# create a Route object for each of the 3 routes   
route1 = Route([depot, weg_east, com_east, ctown, com_west, weg_west, depot], r1d, r1s, number=1)   
route2 = Route([com_east, ctown, com_west, com_east], r2d, r2s, number=2)   
route3 = Route([depot, weg_east, com_east, com_west, weg_west, depot], r3d, r3s, number=3)   
```
### Debugging
PySimio supports command-line debugging by printing each discrete event, processing one event at a time when prompted by the user. 

![Debugging](images/debug.gif)

### Experiments
Comparison of different models can be easily done with PySimio. The `experiment` function returns a DataFrame of the results of each model configuration. 
```Python
SIMULATION_LENGTH = 60*18
ITERATIONS = 20

route1 = [1, 1, 1, 1, 1, 1]
route2 = [2, 2, 2, 2, 2, 2]
route3 = [3, 3, 3, 3, 3, 3]

model1 = create_map(routes_per_bus=[route1, route1, route1, route1, route1, route1, route1], name='700')
model2 = create_map(routes_per_bus=[route1, route1, route1, route1, route1, route2, route3], name='511')
model3 = create_map(routes_per_bus=[route1, route1, route1, route2, route2, route3, route3], name='322')

experiment([model1, model2, model3], SIMULATION_LENGTH, ITERATIONS)
```

### Visualization


## Documentation

