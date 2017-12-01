from pySimio import *
from animation import create_map
import pandas as pd
from multiprocessing import Pool


def thread_process(models):
    """ atomic process computed by each thread """
    # retrieve the arguments from the keyword-arguments
    m = models['model']
    max_time = models['max_time']
    debug = models['debug']
    i = models['i']

    m.simulate(max_time, debug=debug)   # run simulation

    # collect statistics
    stats = m.collect_stats()
    stats["model"] = i

    m.reset()  # reset the simulation
    return stats


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

    for itr in range(iteration):
        thread = Pool(len(models))  # initialize threads for each model
        # create keyword-arguments
        args = [{'model': m, 'debug': debug, 'max_time': max_time, 'results': results, 'i': i}
                for i, m in enumerate(models)]
        stats = thread.map(thread_process, args)  # run multiprocessing

        for s in stats:
            s['iteration'] = itr
        results += stats

        thread.terminate()  # kill the thread

    print(pd.DataFrame(results).sort_values(by='iteration').groupby('model').mean())

    print("experiment done")

    # generate the file
    if output_report:
        out = 'reports/'
        pd.DataFrame(results).to_csv(out + output, index=False)


if __name__ == '__main__':
    num_maps = 3
    maps = []

    model1 = create_map(buses_per_route = (7, 0, 0))
    model2 = create_map(buses_per_route = (7, 0, 0))
    model3 = create_map(buses_per_route = (7, 0, 0))


    for i in range(num_maps):
        maps.append(create_map())

    experiment(maps, 500, 10, output_report=False)
