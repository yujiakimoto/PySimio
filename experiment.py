from pySimio import *
import pandas as pd
from multiprocessing import Pool
from itertools import chain


def create_map(routes_per_bus, arrival_data='data/ArrivalRates.xlsx', name=None):

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

    # route distance data
    r1d = [0.5, 2, 2, 2, 2, 0.5]
    r2d = [2, 2, 0.3]
    r3d = [0.5, 2, 0.3, 2, 0.5]

    # route switch point data
    r1s = {2: {depot: [2.5, 1], weg_east: [2, 1], com_east: [0, 1], ctown: [0, 2], com_west: [5, 1], weg_west: [3, 1]},
           3: {depot: [0, 1], weg_east: [0, 2], com_east: [4, 4], ctown: [2, 4], com_west: [0, 4], weg_west: [0, 0]}}
    r2s = {1: {com_east: [0, 3], ctown: [0, 4], com_west: [0, 5]},
           3: {com_east: [0, 3], ctown: [2, 4], com_west: [0, 4]}}
    r3s = {1: {depot: [0, 1], weg_east: [0, 2], com_east: [0, 3], com_west: [0, 5], weg_west: [0, 0]},
           2: {depot: [2.5, 1], weg_east: [2, 1], com_east: [0, 1], com_west: [5, 1], weg_west: [3, 1]}}

    # create a Route object for each of the 3 routes
    route1 = Route([depot, weg_east, com_east, ctown, com_west, weg_west, depot], r1d, r1s, number=1)
    route2 = Route([com_east, ctown, com_west, com_east], r2d, r2s, number=2)
    route3 = Route([depot, weg_east, com_east, com_west, weg_west, depot], r3d, r3s, number=3)

    # create Bus objects
    # assert(sum(buses_per_route) == 7), "There must be 7 buses total"
    bus_list = []
    bus_num = 1

    for routes_per_hr in routes_per_bus:
        start_route = routes_per_hr[0]
        bus_list.append(Bus(name='Bus'+str(bus_num), route=eval('route'+str(start_route)), schedule=routes_per_hr))
        bus_num += 1

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


def experiment(models, max_time, iteration, output_report=True, output='reports.csv', debug=False, printing=True):
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
    if printing:
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
    if printing:
        print(pd.DataFrame(stats).groupby('model').mean())
        print("experiment done")
    # generate the file
    if output_report:
        out = 'reports/'
        pd.DataFrame(stats).to_csv(out + output, index=False)
    return pd.DataFrame(stats)


if __name__ == '__main__':

    ITERATION = 60*18
    RATE = 7

    # by ratio
    # b1 = [1, 1, 1, 1, 1, 1]
    # b2 = [1, 2, 2, 2, 1, 1]
    # b3 = [1, 2, 2, 2, 2, 1]
    # b4 = [2, 2, 2, 2, 2, 2]
    # b5 = [2, 2, 2, 3, 3, 2]
    # b6 = [3, 2, 2, 3, 3, 2]
    # b7 = [3, 3, 3, 3, 3, 3]

    # # hand picked
    # b41 = [1, 1, 1, 1, 1, 1]
    # b42 = [1, 2, 2, 2, 1, 1]
    # b43 = [3, 2, 2, 2, 2, 1]
    # b44 = [2, 2, 2, 2, 2, 2]
    # b45 = [2, 2, 2, 3, 3, 2]
    # b46 = [3, 3, 2, 3, 3, 3]
    # b47 = [3, 3, 3, 3, 3, 3]

    # shortest queue length
    b1 = [1, 1, 1, 1, 1, 1]
    b2 = [2, 2, 1, 1, 3, 1]
    b3 = [2, 1, 1, 1, 2, 3]
    b4 = [1, 2, 2, 1, 1, 1]
    b5 = [3, 3, 2, 2, 3, 2]
    b6 = [1, 1, 2, 3, 2, 1]
    b7 = [1, 2, 2, 1, 1, 1]

    # shortest avg time
    b51 = [1, 1, 1, 1, 1, 1]
    b52 = [2, 2, 1, 1, 3, 1]
    b53 = [1, 1, 1, 1, 1, 3]
    b54 = [1, 3, 2, 1, 3, 1]
    b55 = [3, 2, 2, 2, 2, 2]
    b56 = [1, 1, 2, 3, 2, 1]
    b57 = [3, 2, 1, 1, 1, 1]

    # lowest hypothermia
    b61 = [1, 1, 1, 1, 1, 1]
    b62 = [1, 2, 2, 2, 3, 1]
    b63 = [3, 1, 1, 1, 1, 1]
    b64 = [1, 3, 2, 3, 2, 2]
    b65 = [2, 2, 1, 2, 1, 1]
    b66 = [1, 1, 1, 2, 3, 1]
    b67 = [1, 2, 2, 2, 3, 3]

    route1 = [1, 1, 1, 1, 1, 1]
    route2 = [2, 2, 2, 2, 2, 2]
    route3 = [3, 3, 3, 3, 3, 3]

    # create map object
    model1 = create_map(routes_per_bus=[route1, route1, route1, route1, route1, route1, route1], name='700')
    model2= create_map(routes_per_bus=[b1, b2, b3, b4, b5, b6, b7], name='opt-queue')
    model3= create_map(routes_per_bus=[b51, b52, b53, b54, b55, b56, b57], name='opt-time')
    model4= create_map(routes_per_bus=[b61, b62, b63, b64, b65, b66, b67], name='opt-2hr')

    model = [model1, model2, model3, model4]

    # run experiment!
    experiment(model, ITERATION, 30, output_report=True, output='out.csv')
