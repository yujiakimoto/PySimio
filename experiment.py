from pySimio import *
from animation import create_map
import pandas as pd
from multiprocessing import Pool


def thread_process(models):
    m = models['model']
    max_time = models['max_time']
    debug = models['debug']
    m.simulate(max_time, debug = debug)
    stats = m.collect_stats()
    stats["model"] = models['i']
    m.reset()
    return stats


def experiment(models, max_time, iteration, output_report = True, output = 'reports.csv', debug = False):
    """ Run the experiment with input models

    Inputs:
        models (list) : list of map objects
        max_time (int) : duration time for each simulation
        iteration (int) : number of experiments to repeat
    """

    assert(all(isinstance(model, Map) for model in models)), "models must be a list of Map objects"

    print ("{} simulations with {} models begins ...".format(iteration, len(models)))
    results = []
    for i in range(iteration):
        thread = Pool(len(models))
        args = [{'model':m, 'debug':debug, 'max_time':max_time, 'results':results, 'i':i} for i, m in enumerate(models)]
        results += thread.map(thread_process, args)

        thread.terminate()

    print (pd.DataFrame(results).head())

    print ("experiment done")

    if output_report:
        out = 'reports/'
        pd.DataFrame(results).to_csv(out + output, index  = False)


if __name__ == '__main__':
    num_map = 3
    maps = []
    for i in range(num_map):
        maps.append(create_map())

    experiment(maps, 500, 10, output_report = False)
