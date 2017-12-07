#!/usr/bin/env python3

import multiprocessing as mp

def cube(x) :
    return {str(x) : x**3}

pool = mp.Pool(processes=4)
results_list = [pool.apply(cube, args=(x,)) for x in range(1,7)] 
results = {}
for result in results_list :
    results = {**results, **result}
print(results)