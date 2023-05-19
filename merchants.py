import numpy as np

from nodes import calculate_value, read_nodes
from sys import stderr

# Remove merchant and its effects from node
# Takes as input the DataFrame of nodes and the name of the node
def remove_merchant(nodes, node):
    nodes.loc[node, 'Merchant'] = False
    nodes.loc[node, 'Steering'][:] = False
    nodes.loc[node, 'Trade Efficiency'] -= 0.1
    nodes.loc[node, 'Power Modifier'] -= 0.05
    nodes.loc[node, 'Our Power'] -= 2

# Add a merchant to a node
# Takes as input the DataFrame of nodes, name of the node to add an to steer to
# If node == to, merchant is set to collect
def add_merchant(nodes, node, to):
    nodes.loc[node, 'Merchant'] = True
    if node != to:
        nodes.loc[node, 'Steering'][:] = [True if s == to else False for s in nodes.loc[node, 'To']]
    nodes.loc[node, 'Trade Efficiency'] += 0.1
    nodes.loc[node, 'Power Modifier'] += 0.05
    nodes.loc[node, 'Our Power'] += 2

# Attempt to optimize home node and merchant placement using a greedy algorithm
def place_merchants(nodes):
    # First remove and count all merchants
    merchants = 0
    for node in nodes[nodes['Merchant']].index:
        remove_merchant(nodes, node)
        merchants += 1
    nodes['Collecting'] = False

    # Iterate through all nodes to find best place to collect
    best_value = 0
    best_home = ""
    for node, data in nodes[nodes['Trade Power'] > 0].iterrows():
        nodes.loc[node, 'Collecting'] = True
        value = calculate_value(nodes)['My Value'].sum()
        print(f'{node}: {value:.3}', file=stderr)
        if value > best_value:
            best_home = node
            best_value = value
        nodes.loc[node, 'Collecting'] = False
    nodes.loc[best_home, 'Collecting'] = True
    print(f'Best home node: {best_home}')

    # Place merchants using a greedy algorithm
    best_value = calculate_value(nodes)['My Value'].sum()
    best_merchants = []
    for _ in range(merchants):
        best_fromto = ()
        for node, data in nodes[~nodes['Merchant'] & nodes['Trade Power'] > 0].iterrows():
            if data['Collecting']:
                # Only set merchants to collect in home node
                add_merchant(nodes, node, node)
                value = calculate_value(nodes)['My Value'].sum()
                if value > best_value:
                    best_fromto = (node, node)
                    best_value = value
                remove_merchant(nodes, node)
            else:
                # Otherwise try steering in every direction
                for to in data['To']:
                    add_merchant(nodes, node, to)
                    value = calculate_value(nodes)['My Value'].sum()
                    if value > best_value:
                        best_fromto = (node, to)
                        best_value = value
                    remove_merchant(nodes, node)
        # Add best merchant and continue
        add_merchant(nodes, best_fromto[0], best_fromto[1])
        best_merchants.append(best_fromto)
    
    # TODO: collecting outside home node

    print('Merchant placement:')
    for node, to in best_merchants:
        print(f'{node} -> {to}')

def main():
    nodes = read_nodes()
    value = calculate_value(nodes)['My Value'].sum()
    print(f'Current profit: {value:.3f} dct')

    place_merchants(nodes)
    value = calculate_value(nodes)['My Value'].sum()
    print(f'Optimized profit: {value:.3f} dct')

if __name__ == '__main__':
    main()
