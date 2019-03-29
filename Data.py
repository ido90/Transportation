import numpy as np
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

# TODO visualize
