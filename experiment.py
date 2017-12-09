from pySimio import *
import pandas as pd
from multiprocessing import Pool
from itertools import chain
from time import time
def create_map(buses_per_route=(7, 0, 0), arrival_data='data/ArrivalRates.xlsx', name=None):

    # create BusStop objects
    depot = BusStop('TDOG Depot')
    weg_east = BusStop('Wegmans-Eastbound')
    weg_west = BusStop('Wegmans-Westbound')
    com_east = BusStop('Commons-Eastbound')
    com_west = BusStop('Commons-Westbound')
    ctown = BusStop('Collegetown')

    # feed arrival rate data to each bus stop
    rates = pd.read_excel(arrival_data)
    weg_east.add_data({com_east: rates['Weg to Com'].values, ctown: rates['Weg to Ctown'].values})
    com_east.add_data({ctown: rates['Com to Ctown'].values})
    com_west.add_data({weg_west: rates['Com to Weg'].values})
    ctown.add_data({com_west: rates['Ctown to Com'].values, weg_west: rates['Ctown to Weg'].values})

    # create a Route object for each of the 3 routes
    route1 = Route([depot, weg_east, com_east, ctown, com_west, weg_west, depot], [0.5, 2, 2, 2, 2, 0.5], 1)
    route2 = Route([com_east, ctown, com_west, com_east], [2, 2, 0.3], 2)
    route3 = Route([depot, weg_east, com_east, com_west, weg_west, depot], [0.5, 2, 2, 2, 0.5], 3)

    # create Bus objects
    # assert(sum(buses_per_route) == 7), "There must be 7 buses total"
    bus_list = []
    bus_num = 1
    for i, num in enumerate(buses_per_route):
        route_num = i + 1
        for j in range(num):
            bus_list.append(Bus('Bus ' + str(bus_num), eval('route' + str(route_num))))
            bus_num += 1
    bus_list = list(reversed(bus_list))

    return Map([route1, route2, route3], bus_list,
               {'TDOG Depot': depot, 'Wegmans-Eastbound': weg_east, 'Wegmans-Westbound': weg_west,
                'Commons-Eastbound': com_east, 'Commons-Westbound': com_west, 'Collegetown': ctown}, name = name)



def thread_process(models):
    """ atomic process computed by each thread """
    # retrieve the arguments from the keyword-arguments
    m = models['model']
    max_time = models['max_time']
    debug = models['debug']
    iteration = models['iteration']

    results = []
    for i in range(iteration):

        m.simulate(max_time, debug=debug)   # run simulation

        # collect statistics
        stats = m.collect_stats()
        stats["model"] = m.name
        stats['iteration']=i

        m.reset()  # reset the simulation

        results.append(stats)

    return results

def model_name(route):
    return str(route[0]) + str(route[1]) + str(route[2])


def experiment(models, max_time, iteration, output_report=True, output='reports.csv', debug=False):
    """ Run the experiment with input models
    Args:
        models (list) : list of map objects
        max_time (int) : duration time for each simulation
        iteration (int) : number of experiments to repeat
        output_report (bool) : if true, generate csv file of simulation results
        output (str) : file name for the simulation output
        debug (bool) : if true, run simulation with DEBUG mode
    """
    assert(all(isinstance(model, Map) for model in models)), "models must be a list of Map objects"
    # begin simulations
    print("{} simulations with {} models begins ...".format(iteration, len(models)))

    # shared variable to combine each simulation results
    results = []


    thread = Pool(len(models))  # initialize threads for each model
    # create keyword-arguments
    args = [{'model': m, 'debug': debug, 'max_time': max_time, 'results': results, 'iteration': iteration}
            for i, m in enumerate(models)]
    stats = thread.map(thread_process, args)  # run multiprocessing

    stats = list(chain(*stats))

    thread.terminate()  # kill the thread



    print(pd.DataFrame(stats).groupby('model').mean())

    print("experiment done")

    # generate the file
    if output_report:
        out = 'reports/'
        pd.DataFrame(stats).to_csv(out + output, index=False)


if __name__ == '__main__':

    ITERATION = 60*18
    RATE = 7
    m1 = (1, 5, 1)
    m2 = (1, 4, 2)
    m3 = (1, 3, 3)
    # m2 = (4, 1, 2)
    # m3 = (4, 1, 1)
    # m3 = (4, 2, 1)
    # m4 = (0, 7, 0)
    # m5 = (1, 1, 5)

    model1 = create_map(buses_per_route = m1, name = model_name(m1))
    model2 = create_map(buses_per_route = m2, name = model_name(m2))
    model3 = create_map(buses_per_route = m3, name = model_name(m3))

    model = [model1, model2, model3]
    experiment(model, ITERATION, 10, output_report=True, output = 'opt.csv')
