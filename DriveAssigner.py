import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Data as D
from time import time
import pickle
from concurrent.futures import ProcessPoolExecutor

class BusSystem:
    def __init__(self, lines, path=None):
        self.lines = lines # BusLines
        if path:
            h = open(path, "rb")
            self.drives = pickle.load(h)
            h.close()
        else:
            self.drives = {}

    def assign_drives(self, drives, save_res=True, distributed=0):
        if distributed:
            tpool = ProcessPoolExecutor(max_workers=distributed)
            ret = tpool.map(self.assign_drive, drives)
            x = list(ret)
        else:
            x = [self.assign_drive(d) for d in drives]

        if save_res:
            self.save_results(x, [d.id for d in drives])

        return x

    def assign_drive(self, drive, save_res=False):
        '''
        drive: a list of tuples (x,y) representing the observed locations.
        return: a sorted list of tuples (MSE, 'shape_id route_id').
        '''
        errs = sorted(self.drive_inconsistencies(drive.points))
        if save_res:
            self.save_results([errs], [drive.id])
        return errs

    def save_results(self, errs, ids, save_full_res=True):
        for id,err in zip(ids, errs):
            errs_route_ids = [ id.split(' ')[1] for score,id in err]
            # filter errors: keep only one Shape ID per each Route ID
            ferrs = [e for i,(e,id) in enumerate(zip(err,errs_route_ids))
                     if id not in set(errs_route_ids[:i]) ]

            self.drives[id] = {'sid': ferrs[0][1].split()[0], 'rid': ferrs[0][1].split()[1],
                               'mse': ferrs[0][0], 'certainty': 1-ferrs[0][0]/ferrs[1][0],
                               'res': (err,ferrs) if save_full_res else None}

    def save_to_file(self, path=r'output/res.pkl'):
        h = open(path, "wb")
        pickle.dump(self.drives, h)
        h.close()

    def drive_inconsistencies(self, drive):
        return [(bus_line.drive_inconsistency(drive), bus_line.id)
                for bus_line in self.lines]

    def print_results(self, only_contradicts=False):
        # print titles
        print('Trip\tDeclared\tEstimated\tMSE\tCertainty\tContradiction')
        # print data
        for k in self.drives:
            if not only_contradicts or \
                            k.split()[1].strip() != self.drives[k]['rid'].strip():
                print('{0:s}\t{1:s}\t{2:s}\t{3:.0f}\t{4:.2f}\t{5:s}'.format(
                    k.split()[0], k.split()[1], self.drives[k]['rid'],
                    self.drives[k]['mse'], self.drives[k]['certainty'],
                    '' if k.split()[1].strip()==self.drives[k]['rid'].strip()
                          or k.split()[1].strip()=='0'
                      else 'CONTRADICTION'))

    def show_drives_errors(self, n=80, vertical_xlabs=True):
        n = n if n<=len(self.drives) else len(self.drives)
        f, axs = plt.subplots(2, 1)
        # 3 best fits (indicating certainty):
        ax = axs[1]
        self.drives_errors_barplot(ax, n, 0, 'green',  'best fit')
        self.drives_errors_barplot(ax, n, 1, 'yellow', '2nd best')
        self.drives_errors_barplot(ax, n, 2, 'red',    '3rd best')
        ax.set_xlabel('Trip ID')
        ax.set_ylabel('RMSE [m]')
        ax.set_xticks(tuple(range(n)))
        ax.set_xticklabels([k.split()[0] for k in self.drives.keys()], fontsize=14)
        if vertical_xlabs:
            for tick in ax.get_xticklabels():
                tick.set_rotation(90)
        ax.legend()
        # 1 best fit (indicating plausibility):
        ax = axs[0]
        self.drives_errors_barplot(ax, n, 0, 'green', 'best fit')
        ax.set_xlabel('Trip ID')
        ax.set_ylabel('RMSE [m]')
        ax.set_title('Errors of Drives with relation to the Likeliest Bus Lines' +
                     ('' if n>=len(self.drives) else
                      '\n(first {0:d} drives out of {1:d})'.format(n,len(self.drives))),
                     fontsize=13)
        ax.set_xticks(tuple(range(n)))
        ax.set_xticklabels([k.split()[0] for k in self.drives.keys()], fontsize=14)
        if vertical_xlabs:
            for tick in ax.get_xticklabels():
                tick.set_rotation(90)
        ax.legend()
        draw()

    def drives_errors_barplot(self, ax, n, ith_best, color, label):
        ax.bar(tuple(range(n)), [self.drives[k]['res'][1][ith_best][0]
                                 for k in list(self.drives.keys())[:n]],
               bottom = [self.drives[k]['res'][1][ith_best-1][0] if ith_best else 0
                         for k in list(self.drives.keys())[:n]],
               color=color, label=label)
        ax.set_xlim([-1,n])

    def summarize_results(self):
        f, axs = plt.subplots(1, 2)
        x = 100 * np.array(list(range(len(self.drives)))) / len(self.drives)
        axs[0].plot(x, sorted([self.drives[k]['mse']
                               for k in self.drives]))
        axs[0].set_title('RMSE Distribution Summary', fontsize=14)
        axs[0].set_xlabel('Drive Percentile [%]', fontsize=12)
        axs[0].set_ylabel('RMSE', fontsize=12)
        axs[0].set_xlim([0,100])
        axs[1].plot(x, sorted([self.drives[k]['certainty']
                               for k in self.drives]))
        axs[1].set_title('Certainties Distribution Summary', fontsize=14)
        axs[1].set_xlabel('Drive Percentile [%]', fontsize=12)
        axs[1].set_ylabel('Certainty: 1 - RMSE1 / RMSE2', fontsize=12)
        axs[1].set_xlim([0,100])
        draw()

    def summarize_inconsistencies(self, drives):
        ids = [k for k in self.drives
               if k.split()[1].strip() != self.drives[k]['rid'].strip()]
        print('\nContradictions: {0:d}'.format(len(ids)))

        if ids:
            drives_orig = self.drives
            self.drives = {k: self.drives[k] for k in ids}

            self.print_results()
            self.show_drives_errors()
            D.show_lines(self.lines, next(d for d in drives if d.id in ids))

            f, axs = plt.subplots(1, 2)
            x = 100 * np.array(list(range(len(self.drives)))) / len(self.drives)
            axs[0].plot(x, sorted([len(d.points) for d in drives if d.id in ids]))
            axs[0].set_title('Trips with Inconsistent Route-ID Assignment',
                             fontsize=14)
            axs[0].set_xlabel('Drive Percentile [%]', fontsize=12)
            axs[0].set_ylabel('Number of GPS observations', fontsize=12)

            mse1 = np.array([self.drives[i]['res'][0][0][0] for i in ids])
            mse2 = np.array(
                [next(self.drives[i]['res'][0][j][0] for j in range(len(self.lines))
                      if self.drives[i]['res'][0][j][1].endswith(i.split()[1]))
                 for i in ids])
            axs[1].plot(x, sorted([1-m1/m2 for m1,m2 in zip(mse1,mse2)]))
            axs[1].set_title('Trips with Inconsistent Route-ID Assignment',
                             fontsize=14)
            axs[1].set_xlabel('Drive Percentile [%]', fontsize=12)
            axs[1].set_ylabel(
                'Adjusted Certainty: 1 - (best RMSE) / (declared route\'s RMSE)',
                fontsize=12)

            self.drives = drives_orig
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
        # a=(a1,a2), b=(b1,b2)
        self.a = a
        self.b = b
        self.ba = subtract(b, a)
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

def draw():
    plt.get_current_fig_manager().window.showMaximized()
    plt.draw()
    plt.pause(1e-17)
    plt.tight_layout()


def main(test=False, fetch_only=True, n=3000, res_path='output/res.pkl'):
    t0 = time()

    # load data
    ll = D.load_lines()
    print('Number of lines: {0:d}.'.format(len(ll)))
    dd = D.load_drives(path='data/test' if test else 'data/train', permit_unlabeled=test)
    print('Number of drive: {0:d}'.format(len(dd)))
    print('Data loaded ({0:.0f} [s]).\n'.format(time()-t0))

    # assign drives
    if fetch_only:
        b = BusSystem(ll, res_path)
    else:
        print('Drives to assign: {0:.0f}.'.format(np.min([n,len(dd)])))
        b = BusSystem(ll)
        b.assign_drives(dd[:n], distributed=5)
        b.save_to_file(res_path)
        print('Drives assigned ({0:.0f} [s]).\n'.format(time()-t0))

    # show results
    b.show_drives_errors(80)
    D.show_lines(ll, dd[0])
    D.show_lines(ll, dd[0], line_nodes=200, drive_points=7)
    b.summarize_results()
    print('Route IDs Reconstruction:')
    b.print_results()
    if not test:
        b.summarize_inconsistencies(dd)

if __name__ == '__main__':
    main(test=False, fetch_only=False, n=3000)
    main(test=True, fetch_only=False, n=3000, res_path='output/test.res.pkl')
    plt.show()
