from pySimio import *
from animation import create_map
import pandas as pd
from multiprocessing import Pool
from itertools import chain


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
    m1 = (7, 0, 0)
    m2 = (5, 1, 1)
    m3 = (3, 2, 2)

    model1 = create_map(buses_per_route = m1, lmbda = RATE, name = model_name(m1)+'-l'+str(RATE))
    model2 = create_map(buses_per_route = m2, lmbda = RATE, name = model_name(m2)+'-l'+str(RATE))
    model3 = create_map(buses_per_route = m3, lmbda = RATE, name = model_name(m3)+'-l'+str(RATE))
    model = [model1, model2, model3]

    experiment(model, ITERATION, 20, output_report=True, output = 'para.csv')
