from experiment import create_map,experiment

def generate_simulation_result(x21,x22,x23,x24,x25,x26,x31,x32,x33,x34,x35,x36,x41,x42,x43,x44,x45,x46,x51,x52,x53,x54,x55,x56,x61,x62,x63,x64,x65,x66,x71,x72,x73,x74,x75,x76):
    b1 = [1, 1, 1, 1, 1, 1]
    b2 = [x21,x22,x23,x24,x25,x26]
    b3 = [x31,x32,x33,x34,x35,x36]
    b4 = [x41,x42,x43,x44,x45,x46]
    b5 = [x51,x52,x53,x54,x55,x56]
    b6 = [x61,x62,x63,x64,x65,x66]
    b7 = [x71,x72,x73,x74,x75,x76]

    model = create_map(routes_per_bus=[b1, b2, b3, b4, b5, b6, b7], name='model')
    return experiment([model], 60*18, 20, output_report=False, printing=False)


def avg_waiting_time(x21,x22,x23,x24,x25,x26,x31,x32,x33,x34,x35,x36,x41,x42,x43,x44,x45,x46,x51,x52,x53,x54,x55,x56,x61,x62,x63,x64,x65,x66,x71,x72,x73,x74,x75,x76):
    stats = generate_simulation_result(x21,x22,x23,x24,x25,x26,x31,x32,x33,x34,x35,x36,x41,x42,x43,x44,x45,x46,x51,x52,x53,x54,x55,x56,x61,x62,x63,x64,x65,x66,x71,x72,x73,x74,x75,x76)
    return stats[stats.keys()[stats.keys().str.contains('waiting time total')]].mean().values.mean()

def avg_queue_length(x21,x22,x23,x24,x25,x26,x31,x32,x33,x34,x35,x36,x41,x42,x43,x44,x45,x46,x51,x52,x53,x54,x55,x56,x61,x62,x63,x64,x65,x66,x71,x72,x73,x74,x75,x76):
    stats = generate_simulation_result(x21,x22,x23,x24,x25,x26,x31,x32,x33,x34,x35,x36,x41,x42,x43,x44,x45,x46,x51,x52,x53,x54,x55,x56,x61,x62,x63,x64,x65,x66,x71,x72,x73,x74,x75,x76)
    return stats[stats.keys()[stats.keys().str.contains('avg people waiting') & ~stats.keys().str.contains('Depot') & ~stats.keys().str.contains('Wegmans-Westbound')]].mean().values.mean()

def avg_occupancy(x21,x22,x23,x24,x25,x26,x31,x32,x33,x34,x35,x36,x41,x42,x43,x44,x45,x46,x51,x52,x53,x54,x55,x56,x61,x62,x63,x64,x65,x66,x71,x72,x73,x74,x75,x76):
    stats = generate_simulation_result(x21,x22,x23,x24,x25,x26,x31,x32,x33,x34,x35,x36,x41,x42,x43,x44,x45,x46,x51,x52,x53,x54,x55,x56,x61,x62,x63,x64,x65,x66,x71,x72,x73,x74,x75,x76)
    return stats[stats.keys()[stats.keys().str.contains('avg occupancy') & stats.keys().str.contains('Bus')]].mean().values.mean()


if __name__ == '__main__':
    print (avg_occupancy(1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))
