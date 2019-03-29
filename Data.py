import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import itertools
import DriveAssigner

def load_drives(path=r'data/train.csv'):
    if not path.endswith('.csv'): path += '.csv'
    return pd.read_csv(path)

def load_lines(path=r'data/shapes.csv'):
    if not path.endswith('.csv'): path += '.csv'
    lines = pd.read_csv(path)

    data = zip(lines.shape_id, lines.shape_pt_lat, lines.shape_pt_lon)
    all_lines = [ DriveAssigner.BusLine(k, [ (lat,lon) for id,lat,lon in giter ])
                  for k,giter in itertools.groupby(data, key=lambda x:x[0]) ]

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
