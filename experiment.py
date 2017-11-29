from pySimio import *

def create_map():

def experiment(models, max_time, iteration):
    """ Run the experiment with input models

    Inputs:
        models (list) : list of map objects
        max_time (int) : duration time for each simulation
        iteration (int) : number of experiments to repeat
    """

    assert(all(isinstance(model, Map) for model in models)), "models must be a list of Map objects"

    for i in range(iteration):



if __name__ == '__main__':
    # number of people (per origin/destination type) to generate and arrival rate
    num_people = 500
    LAMBDA = 5

    # assuming people are reasonable, only 6 possible origin/destination pairs exist
    WegE_ComE = list(np.cumsum(np.random.exponential(LAMBDA, num_people)))
    WegE_Ctown = list(np.cumsum(np.random.exponential(LAMBDA, num_people)))
    ComE_Ctown = list(np.cumsum(np.random.exponential(LAMBDA, num_people)))
    Ctown_ComW = list(np.cumsum(np.random.exponential(LAMBDA, num_people)))
    Ctown_WegW = list(np.cumsum(np.random.exponential(LAMBDA, num_people)))
    ComW_WegW = list(np.cumsum(np.random.exponential(LAMBDA, num_people)))

    # create a BusStop object for each of the 6 bus stops
    TDOG = BusStop('TDOG Depot')
    WegE = BusStop('Wegmans-Eastbound')
    WegW = BusStop('Wegmans-Westbound')
    ComE = BusStop('Commons-Eastbound')
    ComW = BusStop('Commons-Westbound')
    Ctown = BusStop('Collegetown')

    WegE.add_data({ComE: WegE_ComE, Ctown: WegE_Ctown})
    ComE.add_data({Ctown: ComE_Ctown})
    ComW.add_data({WegW: ComW_WegW})
    Ctown.add_data({ComW: Ctown_ComW, WegW: Ctown_WegW})

    # create a Route object for each of the 3 routes
    Route1 = Route([TDOG, WegE, ComE, Ctown, ComW, WegE, TDOG], [0.5, 2, 2, 2, 2, 0.5], 1)
    Route2 = Route([ComE, Ctown, ComW, ComE], [2, 2, 0.3], 2)
    Route3 = Route([TDOG, WegE, ComE, ComW, WegW, TDOG], [0.5, 2, 2, 2, 0.5], 3)

    Bus1 = Bus('Bus 1', Route1)
    Bus2 = Bus('The Kenta Bus', Route2)

    Ithaca = Map([Route1, Route2, Route2], [Bus1, Bus2],
             {'TDOG Depot': TDOG, 'Wegmans-Eastbound': WegE, 'Wegmans-Westbound': WegW,
             'Commons-Eastbound': ComE, 'Commons-Westbound': ComW, 'Collegetown':Ctown})

    Ithaca.simulate(18*60)
