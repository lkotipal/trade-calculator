import numpy as np
import pandas as pd
from nodes import calculate_value, read_nodes

def main():
    nodes = read_nodes()
    value = calculate_value(nodes)['My Value'].sum()
    print(f'Profit: {value:.3f}')
    print()

    h = 0.001
    print('Marginal profit:')
    for node in nodes[nodes['Total Power'] > 0].index:
        print(node)
        nodes.loc[node, 'My Trade Power'] += h
        print(f"1 power gives {(calculate_value(nodes)['My Value'].sum() - value) / h:.3f} dct")
        nodes.loc[node, 'My Trade Power'] -= h

        # Goods produced is given per annum
        nodes.loc[node, 'Local Value'] += h
        print(f"1 value gives {(calculate_value(nodes)['My Value'].sum() - value) / (12 * h):.3f} dct")
        nodes.loc[node, 'Local Value'] -= h
        print()

if __name__ == '__main__':
    main()