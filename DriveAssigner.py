import numpy as np
import pandas as pd

'''
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


--------------- Time complexity ---------------

total computations:       ~1e11
  computations per drive:   ~4e5
    bus lines:                ~100
    intervals per line:       ~40
    points per drive:         ~100
  total drives:             ~3e5
    drives per day:           ~3e3
    total days:               ~90

'''

class BusSystem:
    def __init__(self, line_numbers, lines):
        self.line_numbers = line_numbers # ints
        self.lines = lines # BusLines

    def assign_drive(self, drive):
        '''
        drive: a list of tuples (x,y) representing the observed locations.
        return: line numbers (sorted by probability), corresponding probabilities of bus lines,
                and plausibility of drive wrt most probable bus line.
        '''
        probs,err = self.errors_to_probs(self.drive_inconsistencies(drive))
        # TODO how do I know if it sorts by probs or by line numbers??
        line_numbers,probs = (list(l) for l in zip(*sorted(zip(self.line_numbers,probs))))
        return (line_numbers, probs, err)

    @staticmethod
    def errors_to_probs(logq):
        smallest_inconsistency = np.min(logq) # actually it's the MSE of the drive wrt closest bus line
        logq -= np.min(logq)
        q = np.array([np.exp(lq) if lq>1e-2 else 0 for lq in logq])
        p = q / np.sum(q)
        return (p, np.sqrt(smallest_inconsistency))

    def drive_inconsistencies(self, drive):
        return [bus_line.drive_inconsistency(drive) for bus_line in self.lines]

class BusLine:
    def __init__(self, nodes):
        self.nodes = nodes # list of tuples (x,y)
        self.intervals = self.initialize_intervals()

    def initialize_intervals(self):
        return [Interval(x,y) for x,y in zip(self.nodes[:-1],self.nodes[1:])]

    def drive_inconsistency(self, drive):
        return np.mean([self.sdistance(point) for point in drive])

    def sdistance(self, point):
        return np.min([line.sdistance(point) for line in self.intervals if line.within(point)] +
                      [(point[0]-node[0])**2+(point[1]-node[1])**2 for node in self.nodes])

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
        t = da[0] * self.ba[0] + da[1] * self.ba[1]
        if t <= 0:
            return norm2(da)
        elif t >= self.ba_2:
            db = subtract(point, self.b)
            return norm2(db)
        else:
            return nor2m(da) - t*t / self.ba_2

