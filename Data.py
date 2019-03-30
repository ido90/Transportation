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

def load_drives(path=r'data/train.csv', required_points=25,
                permit_unlabeled=False, plot=True):

    # load from file
    if not path.endswith('.csv'): path += '.csv'
    drives = pd.read_csv(path)

    if permit_unlabeled and 'route_id' not in drives.columns:
        drives['route_id'] = 0

    # convert
    data = zip(drives.trip_index, drives.route_id, drives.lat, drives.lon)
    all_drives = [Drive(k, [to_meters(lat, lon) for id1, id2, lat, lon in giter
                            if lat and lon])
                  for k, giter in itertools.groupby(data,
                                                    key=lambda x:"{} {}".format(x[0],x[1]))]

    # validate tracks lengths
    if plot:
        plot_drives(all_drives, required_points)
    if required_points > 0:
        all_drives = [d for d in all_drives if len(d.points) >= required_points]

    return all_drives

def plot_drives(all_drives, required_points):
    invalid = np.sum([len(d.points) < required_points for d in all_drives])
    f, axs = plt.subplots(1, 1)
    if required_points:
        plt.plot([0, 100], [required_points, required_points],
                 'r-', label='threshold')
    x = 100 * np.array(list(range(len(all_drives)))) / (len(all_drives)-1)
    axs.plot(x, sorted([len(d.points) for d in all_drives]), 'k-')
    axs.set_xlim([0, 100])
    axs.set_xlabel('Drive Percentile [%]', fontsize=12)
    axs.set_ylabel('Number of GPS observations', fontsize=12)
    axs.set_title('Trips Tracks Lengths\n(Invalid lengths: {0:d}/{1:d}={2:.0f}%)'
                  .format(invalid, len(all_drives), 100*invalid/len(all_drives)),
                  fontsize=14)
    axs.legend()
    draw()

def to_meters(lat,lon):
    # Approximations:
    # earth radius ~ 6400km
    # Israel latitude ~ 32 degrees
    # cos(32 degrees) ~ 0.84
    return ((lat - 32) / 180 * np.pi * 6400000,
            (lon - 34) / 180 * np.pi * 6400000 * 0.84)

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
    plt.tight_layout(3)

def show_lines(lines, drive=None, verbose=0, dynamic=False, grid=True,
               line_nodes=10000, drive_points=10000):
    f, axs = plt.subplots(4, ceil(len(lines)/4)) if grid else plt.subplots(1, 1)
    colors = ('b','r','g','y','m','c')
    for i,l in enumerate(lines):
        ax = axs[int(i/4),i%4] if grid else axs
        if verbose>=2:
            print(l.id,colors[i%len(colors)])
        y,x = zip(*l.nodes[:line_nodes])
        x = np.array(x) / 1e3
        y = np.array(y) / 1e3
        ax.plot(np.array(x), np.array(y), colors[i%len(colors)]+'-')
        ax.plot(x[0], y[0], colors[i%len(colors)]+'o', label='start')
        if line_nodes==10000:
            ax.plot(x[-1], y[-1], colors[i%len(colors)]+'x', label='finish')
        if grid:
            ax.set_title('Shape ID: {0:s}, Route ID: {1:s}'
                         .format(l.id.split()[0],l.id.split()[1]), fontsize=10)
            if drive:
                y,x = zip(*drive.points[:drive_points])
                x = np.array(x) / 1e3
                y = np.array(y) / 1e3
                ax.plot(np.array(x), np.array(y), 'k.', label='drive start')
                ax.plot(x[0], y[0], 'ks')
        ax.legend()
        if dynamic:
            draw()
            input('press enter...')
    if (not grid) and drive:
        y, x = zip(*drive.points[:drive_points])
        x = np.array(x) / 1e3
        y = np.array(y) / 1e3
        axs.plot(x, y, 'k.')
        axs.plot(x[0], y[0], 'ks')
    f.suptitle(('A Single Drive vs. ' if drive else '') +
               'All Routes in Database' +
               (' (zoom in beginning of routes)' if line_nodes<10000 else ''),
               fontsize=14)
    draw()

if __name__ == '__main__':
    ll = load_lines()
    show_lines(ll)
    dd = load_drives()
    plt.show()


# Interactively:
'''
import DriveAssigner, Data
system=DriveAssigner.BusSystem(Data.load_lines())
d=Data.load_drives()
system.assign_drive(d[0])
'''
