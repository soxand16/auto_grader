#!/usr/bin/env python3

import multiprocessing as mp
import timeit
import platform
from matplotlib import pyplot as plt
import numpy as np

def print_sysinfo():

    print('\nPython version  :', platform.python_version())
    print('compiler        :', platform.python_compiler())
    print('\nsystem     :', platform.system())
    print('release    :', platform.release())
    print('machine    :', platform.machine())
    print('processor  :', platform.processor())
    print('CPU count  :', mp.cpu_count())
    print('interpreter:', platform.architecture()[0])
    print('\n\n')


n = 1000000000


def rsum(a, b) :
    s = 0
    for i in range(a,b) :
        s += i
    return s

def serial(n):
    print('Running Serial')
    return rsum(1,n)

def multiprocess(processes, n):
    print('Running {} processes'.format(processes))
    r = int(n // processes)
    l = [(i*r+1, (i+1)*r+1) for i in range(processes)]
    pool = mp.Pool(processes=processes)
    data = [pool.apply_async(rsum, args=x) for x in l]
    data = [p.get() for p in data]
    results = sum(data)
    return results


# =============================================================================
# Timing
# =============================================================================

benchmarks = []

benchmarks.append(timeit.Timer('serial(n)',
            'from __main__ import serial, n').timeit(number=1))

benchmarks.append(timeit.Timer('multiprocess(2, n)',
            'from __main__ import multiprocess, n').timeit(number=1))

benchmarks.append(timeit.Timer('multiprocess(3, n)',
            'from __main__ import multiprocess, n').timeit(number=1))

benchmarks.append(timeit.Timer('multiprocess(4, n)',
            'from __main__ import multiprocess, n').timeit(number=1))

benchmarks.append(timeit.Timer('multiprocess(6, n)',
            'from __main__ import multiprocess, n').timeit(number=1))


def plot_results():
    bar_labels = ['serial', '2', '3', '4', '6']

    fig = plt.figure(figsize=(10,6))

    # plot bars
    y_pos = np.arange(len(benchmarks))
    plt.yticks(y_pos, bar_labels, fontsize=16)
    plt.xticks(fontsize=16)
    bars = plt.barh(y_pos, benchmarks,
             align='center', alpha=0.4, color='g')

    # annotation and labels

    for ba,be in zip(bars, benchmarks):
        plt.text(ba.get_width() + 2, ba.get_y() + ba.get_height()/2,
                '{0:.2%}'.format(benchmarks[0]/be),
                ha='center', va='bottom', fontsize=12)

    plt.xlabel('Time, seconds for n=%s' %n, fontsize=16)
    plt.ylabel('Number of Processes', fontsize=16)
#    t = plt.title('Serial vs. Multiprocessing via Array Summing Estimation', fontsize=18)
    plt.ylim([-1,len(benchmarks)])
    plt.xlim([0,max(benchmarks)*1.1])
    plt.vlines(benchmarks[0], -1, len(benchmarks)+0.5, linestyles='dashed')
    plt.grid()
    plt.savefig('speed_comparison.png')
    plt.show()

    
plot_results()
print_sysinfo()

