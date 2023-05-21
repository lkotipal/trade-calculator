import numpy as np
import pandas as pd
from math import sqrt
from nodes import calculate_value, read_nodes
from sys import stderr
from time import time

# Randomize numeric values in the network
def setup(nodes, rng):
    nodes['Local Value'] = rng.uniform(high=10, size=nodes.shape[0])
    nodes['Trade Power'] = rng.uniform(high=1000, size=nodes.shape[0])
    nodes['Collecting Power'] = rng.uniform(size=nodes.shape[0])
    nodes['Transfer Power'] = 1 - nodes['Collecting Power']
    nodes['Power Modifier'] = rng.uniform(size=nodes.shape[0])
    nodes['Our Power'] = rng.uniform(high=100, size=nodes.shape[0])
    nodes['Merchant Power'] = rng.uniform(high=100, size=nodes.shape[0])
    nodes['Trade Efficiency'] = rng.uniform(size=nodes.shape[0])
    nodes['Privateer Efficiency'] = rng.uniform(size=nodes.shape[0])

    nodes['Collecting Power'] = nodes['Trade Power'] * nodes['Collecting Power']
    nodes['Transfer Power'] = nodes['Trade Power'] * nodes['Transfer Power']

def main():
    print(np.__version__, file=stderr)
    print(pd.__version__, file=stderr)
    nodes = read_nodes()
    rng = np.random.default_rng(1444)
    n = 1000
    t = np.zeros(n)
    for i in range(n):
        setup(nodes, rng)
        t0 = time()
        calculate_value(nodes)['My Value'].sum()
        t[i] = time() - t0
    mu = t.mean()
    sigma = t.std(ddof=1)
    # Standard error of mean
    print(f't = {mu} += {sigma / sqrt(n)}')

if __name__ == '__main__':
    main()