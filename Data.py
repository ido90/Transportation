import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import itertools
import DriveAssigner

class Drive:
    def __init__(self, id, points):
        self.id = id
        self.points = points

def load_drives(path=r'data/train.csv'):
    if not path.endswith('.csv'): path += '.csv'
    drives = pd.read_csv(path)

    data = zip(drives.trip_index, drives.route_id, drives.lat, drives.lon)
    all_drives = [ Drive(k, [ (lat,lon) for id1,id2,lat,lon in giter ])
                   for k,giter in itertools.groupby(data, key=lambda x:"{} {}".format(x[0],x[1])) ]

    return all_drives

def load_lines(path=r'data/shapes.csv'):
    if not path.endswith('.csv'): path += '.csv'
    lines = pd.read_csv(path)

    data = zip(lines.shape_id, lines.route_id, lines.shape_pt_lat, lines.shape_pt_lon)
    all_lines = [ DriveAssigner.BusLine(k, [ (lat,lon) for id1,id2,lat,lon in giter ])
                  for k,giter in itertools.groupby(data, key=lambda x:"{} {}".format(x[0],x[1])) ]

    return all_lines

def draw():
    plt.get_current_fig_manager().window.showMaximized()
    plt.draw()
    plt.pause(1e-17)
    plt.tight_layout()

def show_lines(df, verbose=0):
    f, axs = plt.subplots(1, 1)
    colors = ('k','b','r','g','y','m')
    for i,sid in enumerate(np.unique(df.shape_id)):
        if verbose>=2:
            print(i,sid,colors[i%len(colors)])
        axs.plot(df[df.shape_id==sid].shape_pt_lon,
                 df[df.shape_id==sid].shape_pt_lat, colors[i%len(colors)]+'-')
    draw()

if __name__ == '__main__':
    ll = load_lines()
    show_lines(ll, verbose=2)
    plt.show()
