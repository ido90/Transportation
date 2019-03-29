import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Data as D
from time import time
from concurrent.futures import ProcessPoolExecutor

'''
TODO:
1. understand the definition of the problem & give full end-to-end solution
2. time optimization
3. improve algo to include directions

--------------- Data assumptions ---------------

1. Bus-lines are available as a list of line-numbers along with the corresponding paths.
Each path is available as a list of 2D points (representing the locations of the stations).

2. Drives observations are available as a list of separated drives,
each containing a list of 2D locations along with the corresponding times.


--------------- Model assumptions ---------------

1. The probability of observation of a bus in distance d from the line goes like exp(-d^2),
expressing GPS errors, map inaccuracies, and actual deviations from the planned road.

Note: that's a quite arbitrary-scale assumption, since the basis of the exponent e,
determines the ratio between probabilities. This will be a problem when estimating the
gap between the probabilities. However, it does not affect the identity of the ML line.

Note: the ML line is actually the one that minimizes the MSE.

2. The prior probability for all the lines is identical. Alternatively,
we look for ML line given the observation, rather than max-probability line.

3. The roads between the stations can be approximated as straight lines:
the distance between the actual road and the straight line,
is negligible compared to the distance between roads of two different buses.


--------------- Possible improvements ---------------

1. Temporal direction of the bus line is currently not exploited, and really should be.

Simple exploitation: at each point, note which interval is the closest, and if the intervals
are not monotonous, then reduce probability. Drawback: closest interval may be just a close interval,
where the actual interval of the drive is adjacent. So assigning the other,
slightly more distant interval could be better, hence we don't really maximize the likelihood.
 
Advanced exploitation: choose best assignment of intervals under constraint of monotony, eg using DP. 

2. Running time optimization: remove most of the lines at early stage (eg using beginning and end),
and possibly remove more as the process goes on (eg improve resolution of points
instead of going over points sequentially).


--------------- Time complexity estimation ---------------

total computations:       ~1e11
  computations per drive:   ~4e5
    bus lines:                ~100
    intervals per line:       ~40
    points per drive:         ~100
  total drives:             ~3e5
    drives per day:           ~3e3
    total days:               ~90

'''

def draw():
    plt.get_current_fig_manager().window.showMaximized()
    plt.draw()
    plt.pause(1e-17)
    plt.tight_layout()

class BusSystem:
    def __init__(self, lines):
        self.lines = lines # BusLines
        self.drives = {}

    def assign_drive(self, drive, save_full_res=True):
        '''
        drive: a list of tuples (x,y) representing the observed locations.
        return: line numbers (sorted by probability), corresponding probabilities of bus lines,
                and plausibility of drive wrt most probable bus line.
        '''
        errs = sorted(self.drive_inconsistencies(drive.points))
        errs_route_ids = [ id.split(' ')[1] for score,id in errs ]
        ferrs = [ e for i,(e,id) in enumerate(zip(errs,errs_route_ids)) if id not in set(errs_route_ids[:i]) ]
        # save results
        self.drives[drive.id] = {'sid': ferrs[0][1].split()[0], 'rid': ferrs[0][1].split()[1],
                                 'mse': ferrs[0][0], 'certainty': 1-ferrs[0][0]/ferrs[1][0],
                                 'res': (errs,ferrs) if save_full_res else None}
        return errs
        #probs,err = self.errors_to_probs(self.drive_inconsistencies(drive))
        #line_numbers,probs = (list(l) for l in zip(*sorted(zip(self.line_numbers,probs))))
        # how do I know if it sorts by probs or by line numbers??
        #return (line_numbers, probs, err)

    @staticmethod
    def errors_to_probs(logq):
        smallest_inconsistency = np.min(logq) # actually it's the MSE of the drive wrt closest bus line
        logq -= np.min(logq)
        q = np.array([np.exp(lq) if lq>1e-2 else 0 for lq in logq])
        p = q / np.sum(q)
        return (p, np.sqrt(smallest_inconsistency))

    def drive_inconsistencies(self, drive):
        return [(bus_line.drive_inconsistency(drive), bus_line.id) for bus_line in self.lines]

    def show_drives_errors(self, n=np.inf, n_fits=3, vertical_xlabs=True):
        n = n if n<=len(self.drives) else len(self.drives)
        f, axs = plt.subplots(1, 1)
        ax = axs
        if n_fits>=3:
            ax.bar(tuple(range(n)), [self.drives[k]['res'][1][2][0] for k in list(self.drives.keys())[:n]],
                   color='red', label='3rd best')
        if n_fits>=2:
            ax.bar(tuple(range(n)), [self.drives[k]['res'][1][1][0] for k in list(self.drives.keys())[:n]],
                   color='yellow', label='2nd best')
        ax.bar(tuple(range(n)), [self.drives[k]['res'][1][0][0] for k in list(self.drives.keys())[:n]],
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
    ll = D.load_lines()
    print('Number of lines: {0:d}.'.format(len(ll)))
    dd = D.load_drives()
    print('Number of drive: {0:d}'.format(len(dd)))
    print('Data loaded ({0:.0f} [s]).'.format(time()-t0))
    n = 2
    print('Drives to assign: {0:d}.'.format(n))
    b = BusSystem(ll)

    tpool = ProcessPoolExecutor(max_workers=3)
    ret = tpool.map(b.assign_drive, dd[:n])
    x = list(ret)
    #x = [b.assign_drive(d) for d in dd[:n]]

    print('Drives assigned ({0:.0f} [s]).'.format(time()-t0))
    b.show_drives_errors()
    b.show_drives_errors(n_fits=2)
    b.show_drives_errors(n_fits=1)
    D.show_lines(ll, dd[2])
    D.show_lines(ll, dd[2], line_nodes=100, drive_points=7)
    plt.show()
