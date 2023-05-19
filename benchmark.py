import numpy as np
import pandas as pd
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
    nodes['Trade Efficiency'] = rng.uniform(size=nodes.shape[0])
    nodes['Privateer Efficiency'] = rng.uniform(size=nodes.shape[0])

    nodes['Collecting Power'] = nodes['Trade Power'] * nodes['Collecting Power']
    nodes['Transfer Power'] = nodes['Trade Power'] * nodes['Transfer Power']
    nodes['Merchant Power'] = nodes['Merchant Power'].apply(lambda x: rng.dirichlet(np.ones_like(x)))
    nodes['Merchant Power'] = nodes['Transfer Power'] * nodes['Merchant Power'] # TODO THIS IS WRONG :D

def main():
    nodes = read_nodes()
    rng = np.random.default_rng(1444)
    number = 100
    t = 0
    for i in range(number):
        print(i, file=stderr)
        setup(nodes, rng)
        t0 = time()
        calculate_value(nodes)['My Value'].sum()
        t += time() - t0
    print(t / number)

if __name__ == '__main__':
    main()