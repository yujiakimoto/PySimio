import numpy as np
import pandas as pd


def generate_arrival(rates, interval = 180):
    """generate the data based on arrival rate (# arrival / hour)
    Args:
        rates (list) : list of arrival rate
        interval (int) : when the arrival is non-stationary, decides the interval to
        update the lambda. Default is 180 (up date every 3 hour)
    """
    current_time = 0
    current_idx = 0
    arrival_data = []
    # loop until the rates exhausts
    while current_idx < len(rates):
        c = 0
        # refresh every interval
        while current_time < interval * (current_idx+1):
            inter_arrival = np.random.exponential(1/(rates[current_idx]/60))
            current_time += inter_arrival
            arrival_data.append(current_time)
            c += 1
        current_idx += 1
    return np.array(arrival_data)

if __name__ == '__main__':
    rates = pd.read_excel('data/ArrivalRates.xlsx')
    # weg - com
    weg_com = generate_arrival(rates['Weg to Com'].values)
    # weg - ctown
    weg_ctown = generate_arrival(rates['Weg to Ctown'].values)
    # com - ctown
    com_ctown = generate_arrival(rates['Com to Ctown'].values)
    # com - weg
    com_weg = generate_arrival(rates['Com to Weg'].values)
    # ctown - weg
    ctown_weg = generate_arrival(rates['Ctown to Weg'].values)
    # ctown - com
    ctown_com = generate_arrival(rates['Ctown to Com'].values)
