import pysmac
from experiment import create_map

def avg_waiting_time(x21,x22,x23,x24,x25,x26,x31,x32,x33,x34,x35,x36,x41,x42,x43,x44,x45,x46,x51,x52,x53,x54,x55,x56,x61,x62,x63,x64,x65,x66,x71,x72,x73,x74,x75,x76):
    b1 = [1, 1, 1, 1, 1, 1]
    b2 = [x21,x22,x23,x24,x25,x26]
    b3 = [x31,x32,x33,x34,x35,x36]
    b4 = [x41,x42,x43,x44,x45,x46]
    b5 = [x51,x52,x53,x54,x55,x56]
    b6 = [x61,x62,x63,x64,x65,x66]
    b7 = [x71,x72,x73,x74,x75,x76]

    model = create_map(routes_per_bus=[route1, route1, route1, route1, route1, route1, route1], name='model')


def avg_queue_length():
    pass


def avg_occupancy():
    pass


if __name__ == "__main__":

    parameters = dict(
        x21=('categorical', [1, 2, 3], 1), x22=('categorical', [1, 2, 3], 1), x23=('categorical', [1, 2, 3], 1),
        x24=('categorical', [1, 2, 3], 1), x25=('categorical', [1, 2, 3], 1), x26=('categorical', [1, 2, 3], 1),
        x31=('categorical', [1, 2, 3], 1), x32=('categorical', [1, 2, 3], 1), x33=('categorical', [1, 2, 3], 1),
        x34=('categorical', [1, 2, 3], 1), x35=('categorical', [1, 2, 3], 1), x36=('categorical', [1, 2, 3], 1),
        x41=('categorical', [1, 2, 3], 1), x42=('categorical', [1, 2, 3], 1), x43=('categorical', [1, 2, 3], 1),
        x44=('categorical', [1, 2, 3], 1), x45=('categorical', [1, 2, 3], 1), x46=('categorical', [1, 2, 3], 1),
        x51=('categorical', [1, 2, 3], 1), x52=('categorical', [1, 2, 3], 1), x53=('categorical', [1, 2, 3], 1),
        x54=('categorical', [1, 2, 3], 1), x55=('categorical', [1, 2, 3], 1), x56=('categorical', [1, 2, 3], 1),
        x61=('categorical', [1, 2, 3], 1), x62=('categorical', [1, 2, 3], 1), x63=('categorical', [1, 2, 3], 1),
        x64=('categorical', [1, 2, 3], 1), x65=('categorical', [1, 2, 3], 1), x66=('categorical', [1, 2, 3], 1),
    )

    opt = pysmac.SMAC_optimizer()
    value, parameters = opt.minimize(avg_waiting_time, 100, parameters)

    print(('Lowest function value found: %f' % value))
    print(('Parameter setting %s' % parameters))
