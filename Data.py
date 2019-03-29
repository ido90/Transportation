import numpy as np
import pandas as pd

def load_drives(path=r'data/train.csv'):
    if not path.endswith('.csv'): path += '.csv'
    return pd.read_csv(path)

def load_lines(path=r'data/shapes.csv'):
    if not path.endswith('.csv'): path += '.csv'
    return pd.read_csv(path)

# TODO visualize
