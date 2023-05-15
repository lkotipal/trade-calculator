import numpy as np
import pandas as pd

from nodes import calculate_value, read_nodes

def remove_merchant(nodes, node):
    nodes.loc[node, 'Merchant'] = False
    nodes.loc[node, 'Steering'][:] = False
    nodes.loc[node, 'Trade Efficiency'] -= 0.1
    nodes.loc[node, 'Power Modifier'] -= 0.05
    nodes.loc[node, 'Our Power'] -= 2

def add_merchant(nodes, node, to):
    nodes.loc[node, 'Merchant'] = True
    if node != to:
        nodes.loc[node, 'Steering'][:] = [True if s == to else False for s in nodes.loc[node, 'To']]
    nodes.loc[node, 'Trade Efficiency'] += 0.1
    nodes.loc[node, 'Power Modifier'] += 0.05
    nodes.loc[node, 'Our Power'] += 2

def place_merchants(nodes):
    merchants = 0
    for node in nodes[nodes['Merchant']].index:
        remove_merchant(nodes, node)
        merchants += 1

    # Greedy algorithm
    best_value = calculate_value(nodes)['My Value'].sum()
    best_merchants = []
    for _ in range(merchants):
        best_fromto = ()
        for node, data in nodes[~nodes['Merchant'] & nodes['Trade Power'] > 0].iterrows():
            if data['Collecting']:
                add_merchant(nodes, node, node)
                value = calculate_value(nodes)['My Value'].sum()
                if value > best_value:
                    best_fromto = (node, node)
                    best_value = value
                remove_merchant(nodes, node)
            else:
                for to in data['To']:
                    add_merchant(nodes, node, to)
                    value = calculate_value(nodes)['My Value'].sum()
                    if value > best_value:
                        best_fromto = (node, to)
                        best_value = value
                    remove_merchant(nodes, node)
        add_merchant(nodes, best_fromto[0], best_fromto[1])
        best_merchants.append(best_fromto)
    
    # TODO: collection

    print('Merchant placement:')
    for node, to in best_merchants:
        print(f'{node} -> {to}')

def main():
    nodes = read_nodes()
    value = calculate_value(nodes)['My Value'].sum()
    print(f'Profit: {value:.3f} dct')
    print()

    place_merchants(nodes)
    value = calculate_value(nodes)['My Value'].sum()
    print(f'Profit: {value:.3f} dct')
    print()

if __name__ == '__main__':
    main()
