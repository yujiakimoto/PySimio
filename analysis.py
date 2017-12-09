import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os

def draw_time_series(df, directory = None, save = False):
    df_time = df[df.keys()[df.keys().str.contains('hourly') & ~df.keys().str.contains('Depot') & ~df.keys().str.contains('Wegmans-West')]]

    for k in df_time.keys():
        data = []
        for i in df_time[k].values:
            data.append(np.fromstring(i, dtype=np.float, sep=' '))
        df_time[k] = data

    df_time['model'] = df['model']
    df_data = []

    for i, data in df_time.iterrows():
        dict_point = {}
        for k in data.keys():
            if k != 'model':
                for hour,obs in enumerate(data[k]):
                    df_data.append({'stats':k, 'hour':hour, 'observation': obs, 'simulation' : i, 'model' : data['model']})
    tf = pd.DataFrame(df_data)

    for k in list(set(tf['stats'])):
        tmp = tf[tf['stats'] == k]
        plt.title(k)
        ax = sns.tsplot(time="hour", value="observation", unit = 'simulation', condition="model",data=tmp, err_style="ci_bars")
        if save:
            if not os.path.exists(directory):
                os.makedirs(directory)
            plt.savefig(directory + '/' + k + '.png')
        plt.show()


def draw_smore(df, directory = None, save = False):
    df_smore = df[df.keys()[~df.keys().str.contains('distance') & \
                            ~df.keys().str.contains('hourly') & \
                            ~df.keys().str.contains('Depot') & \
                            ~df.keys().str.contains('Wegmans-West') &\
                            ~df.keys().str.contains('iteration')]]

    for k in df_smore.keys():
        if k != 'model':
            plt.title(k)
            ax = sns.boxplot(x="model", y=k, data=df_smore)
            if save:
                if not os.path.exists(directory):
                    os.makedirs(directory)
                plt.savefig(directory + '/' + k + '.png')
            plt.show()
