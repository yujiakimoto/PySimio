from pySimio import *
from animation import create_map
import pandas as pd

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
        for i, m in enumerate(models):
            m.simulate(max_time, debug = debug)
            stats = m.collect_stats()
            stats["model"] = i
            results.append(stats)
            m.reset()

    print (pd.DataFrame(results).groupby('model').mean())

    print ("experiment done")

    if output_report:
        out = 'reports/'
        pd.DataFrame(results).to_csv(out + output, index  = False)


if __name__ == '__main__':
    num_map = 3
    maps = []
    for i in range(num_map):
        maps.append(create_map())

    experiment(maps, 500, 5, output_report = False)
