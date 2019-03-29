import numpy as np
import pandas as pd

def load_drives(path=r'D:\Code\Python\Transportation\Data\train.csv'):
    if not path.endswith('.csv'): path += '.csv'
    return pd.read_csv(path)

def load_lines(path=r'D:\Code\Python\Transportation\Data\shapes.csv'):
    if not path.endswith('.csv'): path += '.csv'
    return pd.read_csv(path)

# TODO visualize