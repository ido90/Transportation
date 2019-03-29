import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from math import ceil
import itertools
import DriveAssigner

class Drive:
    def __init__(self, id, points):
        self.id = id
        self.points = points

def to_meters(lat,lon):
    # aprox
    # earth radius = 6400km
    # cos(34 degrees) = 0.83
    return ((lat - 32) / 180 * np.pi * 6400000,
            (lon - 34) / 180 * np.pi * 6400000 * 0.83)

def load_drives(path=r'data/train.csv'):
    if not path.endswith('.csv'): path += '.csv'
    drives = pd.read_csv(path)

    data = zip(drives.trip_index, drives.route_id, drives.lat, drives.lon)
    all_drives = [ Drive(k, [ to_meters(lat,lon) for id1,id2,lat,lon in giter ])
                   for k,giter in itertools.groupby(data, key=lambda x:"{} {}".format(x[0],x[1])) ]

    return all_drives

def load_lines(path=r'data/shapes.csv'):
    if not path.endswith('.csv'): path += '.csv'
    lines = pd.read_csv(path)

    data = zip(lines.shape_id, lines.route_id, lines.shape_pt_lat, lines.shape_pt_lon)
    all_lines = [ DriveAssigner.BusLine(k, [ to_meters(lat,lon) for id1,id2,lat,lon in giter ])
                  for k,giter in itertools.groupby(data, key=lambda x:"{} {}".format(x[0],x[1])) ]

    return all_lines

def draw():
    plt.get_current_fig_manager().window.showMaximized()
    plt.draw()
    plt.pause(1e-17)
    plt.tight_layout()

def show_lines(lines, drive=None, verbose=0, dynamic=False, grid=True,
               line_nodes=10000, drive_points=10000):
    f, axs = plt.subplots(4, ceil(len(lines)/4)) if grid else plt.subplots(1, 1)
    colors = ('b','r','g','y','m','c')
    for i,l in enumerate(lines):
        ax = axs[int(i/4),i%4] if grid else axs
        if verbose>=2:
            print(l.id,colors[i%len(colors)])
        y,x = zip(*l.nodes[:line_nodes])
        ax.plot(x, y, colors[i%len(colors)]+'-')
        ax.plot(x[0], y[0], colors[i%len(colors)]+'o')
        ax.plot(x[-1], y[-1], colors[i%len(colors)]+'x')
        if grid and drive:
            y,x = zip(*drive.points[:drive_points])
            ax.plot(x, y, 'k.')
            ax.plot(x[0], y[0], 'ks')
        if dynamic:
            draw()
            input('press enter...')
    if (not grid) and drive:
        y, x = zip(*drive.points[:drive_points])
        axs.plot(x, y, 'k.')
        axs.plot(x[0], y[0], 'ks')
    draw()

if __name__ == '__main__':
    ll = load_lines()
    show_lines(ll[5:8], grid=0, verbose=2)
    plt.show()