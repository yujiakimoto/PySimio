import sys
import numpy as np
from pySimio import *


def create_map(arrival_rates=None):

    if arrival_rates is None:
        rate = 5
        num_people = 20

        WegE_ComE = list(np.cumsum(np.random.exponential(rate, num_people)))
        WegE_Ctown = list(np.cumsum(np.random.exponential(rate, num_people)))
        ComE_Ctown = list(np.cumsum(np.random.exponential(rate, num_people)))
        Ctown_ComW = list(np.cumsum(np.random.exponential(rate, num_people)))
        Ctown_WegW = list(np.cumsum(np.random.exponential(rate, num_people)))
        ComW_WegW = list(np.cumsum(np.random.exponential(rate, num_people)))

    else:
        WegE_ComE, WegE_Ctown, ComE_Ctown, Ctown_ComW, Ctown_WegW, ComW_WegW = arrival_rates

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

    Ithaca = Map([Route1, Route2, Route3], [Bus1, Bus2],
                 {'TDOG Depot': TDOG, 'Wegmans-Eastbound': WegE, 'Wegmans-Westbound': WegW,
                  'Commons-Eastbound': ComE, 'Commons-Westbound': ComW, 'Collegetown': Ctown})
    
    return Ithaca


if __name__ == "__main__":
    create_map()