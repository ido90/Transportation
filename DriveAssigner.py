import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Data as D
from time import time
from concurrent.futures import ProcessPoolExecutor
import pickle

'''
TODO:
1. time optimization
2. improve algo to include directions
'''

def draw():
    plt.get_current_fig_manager().window.showMaximized()
    plt.draw()
    plt.pause(1e-17)
    plt.tight_layout()

class BusSystem:
    def __init__(self, lines, path=None):
        self.lines = lines # BusLines
        if path:
            h = open(path, "rb")
            x = pickle.load(h)
            h.close()
            self.drives = x.drives
        else:
            self.drives = {}

    def assign_drive(self, drive, save_res=False):
        '''
        drive: a list of tuples (x,y) representing the observed locations.
        return: line numbers (sorted by probability), corresponding probabilities of bus lines,
                and plausibility of drive wrt most probable bus line.
        '''
        errs = sorted(self.drive_inconsistencies(drive.points))
        if save_res:
            self.save_results([errs], [drive.id])
        return errs
        #probs,err = self.errors_to_probs(self.drive_inconsistencies(drive))
        #line_numbers,probs = (list(l) for l in zip(*sorted(zip(self.line_numbers,probs))))
        # how do I know if it sorts by probs or by line numbers??
        #return (line_numbers, probs, err)

    def save_results(self, errs, ids, save_full_res=True):
        for id,err in zip(ids, errs):
            errs_route_ids = [ id.split(' ')[1] for score,id in err]
            ferrs = [e for i,(e,id) in enumerate(zip(err,errs_route_ids))
                     if id not in set(errs_route_ids[:i]) ]
            self.drives[id] = {'sid': ferrs[0][1].split()[0], 'rid': ferrs[0][1].split()[1],
                                     'mse': ferrs[0][0], 'certainty': 1-ferrs[0][0]/ferrs[1][0],
                                     'res': (err,ferrs) if save_full_res else None}

    def save_to_file(self, path=r'data/res.pkl'):
        h = open(path, "wb")
        pickle.dump(self.drives, h)
        h.close()

    @staticmethod
    def errors_to_probs(logq):
        smallest_inconsistency = np.min(logq)
        # actually above it's the MSE of the drive wrt closest bus line
        logq -= np.min(logq)
        q = np.array([np.exp(lq) if lq>1e-2 else 0 for lq in logq])
        p = q / np.sum(q)
        return (p, np.sqrt(smallest_inconsistency))

    def drive_inconsistencies(self, drive):
        return [(bus_line.drive_inconsistency(drive), bus_line.id) for bus_line in self.lines]

    def show_drives_errors(self, n=np.inf, vertical_xlabs=True):
        n = n if n<=len(self.drives) else len(self.drives)
        f, axs = plt.subplots(2, 1)
        ax = axs[1]
        ax.bar(tuple(range(n)), [self.drives[k]['res'][1][2][0]
                                 for k in list(self.drives.keys())[:n]],
               color='red', label='3rd best')
        ax.bar(tuple(range(n)), [self.drives[k]['res'][1][1][0]
                                 for k in list(self.drives.keys())[:n]],
               color='yellow', label='2nd best')
        ax.bar(tuple(range(n)), [self.drives[k]['res'][1][0][0]
                                 for k in list(self.drives.keys())[:n]],
               color='green', label='best fit')
        ax.set_xlabel('Trip ID')
        ax.set_ylabel('MSE [m]')
        ax.set_xticks(tuple(range(n)))
        ax.set_xticklabels(self.drives.keys(), fontsize=14)
        if vertical_xlabs:
            for tick in ax.get_xticklabels():
                tick.set_rotation(90)
        ax.legend()
        ax = axs[0]
        ax.bar(tuple(range(n)), [self.drives[k]['res'][1][0][0]
                                 for k in list(self.drives.keys())[:n]],
               color='green', label='best fit')
        ax.set_xlabel('Trip ID')
        ax.set_ylabel('MSE [m]')
        ax.set_xticks(tuple(range(n)))
        ax.set_xticklabels(self.drives.keys(), fontsize=14)
        if vertical_xlabs:
            for tick in ax.get_xticklabels():
                tick.set_rotation(90)
        ax.legend()
        draw()

class BusLine:
    def __init__(self, id, nodes):
        self.id = id
        self.nodes = nodes # list of tuples (x,y)
        self.intervals = self.initialize_intervals()

    def initialize_intervals(self):
        return [Interval(x,y) for x,y in zip(self.nodes[:-1],self.nodes[1:])]

    def drive_inconsistency(self, drive):
        return np.sqrt(np.mean([self.sdistance(point) for point in drive]))
        # Note: MSE might not be sensitive enough to outliers

    def sdistance(self, point):
        return np.min([line.sdistance(point) for line in self.intervals])

def subtract(p1, p2):
    return (p1[0] - p2[0], p1[1] - p2[1])
def inner_product(p1, p2):
    return p1[0]*p2[0] + p1[1]*p2[1]
def norm2(p):
    return inner_product(p,p)

class Interval:
    def __init__(self, a, b):
        # a=(a1,a2), b=(b1,b2); should represent the line conveniently for the other methods
        self.a = a
        self.b = b
        self.ba = subtract(b, b)
        self.ba_2 = norm2(self.ba)

    def sdistance(self, point):
        da = subtract(point, self.a)
        t = inner_product(da, self.ba)
        if t <= 0:
            return norm2(da)
        elif t >= self.ba_2:
            db = subtract(point, self.b)
            return norm2(db)
        else:
            return norm2(da) - t*t / self.ba_2

if __name__ == '__main__':
    t0 = time()
    # load data
    ll = D.load_lines()
    print('Number of lines: {0:d}.'.format(len(ll)))
    dd = D.load_drives()
    print('Number of drive: {0:d}'.format(len(dd)))
    print('Data loaded ({0:.0f} [s]).\n'.format(time()-t0))
    # assign drives
    distributed = True
    n = 200
    print('Drives to assign: {0:d}.'.format(n))
    b = BusSystem(ll)
    if distributed:
        tpool = ProcessPoolExecutor(max_workers=5)
        ret = tpool.map(b.assign_drive, dd[:n])
        x = list(ret)
    else:
        x = [b.assign_drive(d) for d in dd[:n]]
    b.save_results(x, [d.id for d in dd[:n]])
    print('Drives assigned ({0:.0f} [s]).\n'.format(time()-t0))
    # show results
    b.show_drives_errors()
    D.show_lines(ll, dd[2])
    #D.show_lines(ll, dd[2], line_nodes=200, drive_points=7)
    print('Route IDs Reconstruction:')
    print('Trip\tDeclared\tEstimated\tMSE\tCertainty\tContradiction')
    for k in b.drives:
        print('{0:s}\t{1:s}\t{2:s}\t{3:.0f}\t{4:.2f}\t{5:s}'.format(
            k.split()[0], k.split()[1], b.drives[k]['rid'],
            b.drives[k]['mse'], b.drives[k]['certainty'],
            '' if k.split()[1].strip()==b.drives[k]['rid'].strip() else 'CONTRADICTION' ) )
    ids = [k for k in b.drives if k.split()[1].strip()!=b.drives[k]['rid'].strip()]
    b.save_to_file()
    print('\nContradictions: {0:d}'.format(len(ids)))
    b.drives = {k: b.drives[k] for k in ids}
    b.show_drives_errors()
    D.show_lines(ll, dd[0])
    D.show_lines(ll, dd[1])
    D.show_lines(ll, dd[-1])
    for k in b.drives:
        print('{0:s}\t{1:s}\t{2:s}\t{3:.0f}\t{4:.2f}\t'.format(
            k.split()[0], k.split()[1], b.drives[k]['rid'],
            b.drives[k]['mse'], b.drives[k]['certainty'] ) )
    plt.show()
